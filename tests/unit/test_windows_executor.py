import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from threading import Event
from unittest.mock import patch

from troubleshoot.contracts import ContractError
from troubleshoot.windows.policy import ExecutionContext
from troubleshoot.windows.registry import WindowsExecutor
from troubleshoot.windows.runner import NativeError, PowerShellWorker


class Worker:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def run(self, worker, operation, payload):
        self.calls.append(operation)
        reply = next(self.replies)
        if isinstance(reply, Exception):
            raise reply
        return reply


def context(mode='repair', approval=lambda request: True):
    return ExecutionContext('run', 'action', mode, Event(), approval)


class WindowsTests(unittest.TestCase):
    def test_no_model_command_or_extra_arguments(self):
        executor = WindowsExecutor(Worker([]))
        for operation, arguments in [('shell', {}), ('system_snapshot', {'command': 'whoami'})]:
            with self.assertRaises(ContractError):
                executor.diagnose(operation, arguments)

    def test_diagnose_mode_never_mutates(self):
        worker = Worker([{'status': 'Stopped'}])
        result = WindowsExecutor(worker).start_spooler({}, context('diagnose'))
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(worker.calls, ['spooler_status'])

    def test_denial_and_nonboolean_approval(self):
        for approval in (None, lambda request: False, lambda request: 1):
            worker = Worker([{'status': 'Stopped'}])
            self.assertEqual(WindowsExecutor(worker).start_spooler({}, context(approval=approval)).status, 'blocked')
            self.assertEqual(worker.calls, ['spooler_status'])

    def test_cancel_during_approval(self):
        ctx = context()
        def approve(request):
            ctx.cancelled.set()
            return True
        ctx.consume_authorization = approve
        worker = Worker([{'status': 'Stopped'}])
        self.assertEqual(WindowsExecutor(worker).start_spooler({}, ctx).status, 'blocked')
        self.assertEqual(len(worker.calls), 1)

    def test_approval_bound_to_state(self):
        ctx = context()
        a = ctx.require_mutation('start_spooler', {}, {'status': 'Stopped'}, 'start')
        b = ctx.require_mutation('start_spooler', {}, {'status': 'Running'}, 'start')
        self.assertNotEqual(a.fingerprint, b.fingerprint)

    def test_running_service_not_modified(self):
        worker = Worker([{'status': 'Running'}])
        self.assertEqual(WindowsExecutor(worker).start_spooler({}, context()).status, 'blocked')
        self.assertEqual(len(worker.calls), 1)

    def test_missing_durable_storage_blocks_repair(self):
        worker = Worker([{'status': 'Stopped'}])
        self.assertEqual(WindowsExecutor(worker).start_spooler({}, context()).status, 'blocked')
        self.assertEqual(len(worker.calls), 1)

    def test_success_checks_fresh_status_and_limits_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = Worker([{'status': 'Stopped'}, {'changed': True}, {'status': 'Running'}])
            result = WindowsExecutor(worker, Path(directory)).start_spooler({}, context())
            self.assertEqual(result.status, 'ok')
            self.assertIn('actual print', result.limitations[0])
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_failure_after_confirmed_change_recovers(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = Worker([{'status': 'Stopped'}, {'changed': True}, {'status': 'Stopped'}, {}, {'status': 'Stopped'}])
            result = WindowsExecutor(worker, Path(directory)).start_spooler({}, context())
            self.assertTrue(result.evidence['recovered'])
            self.assertFalse(result.changed)
            self.assertIn('restore_spooler_stopped', worker.calls)

    def test_uncertain_timeout_does_not_blindly_stop_service(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = Worker([{'status': 'Stopped'}, NativeError('timeout')])
            result = WindowsExecutor(worker, Path(directory)).start_spooler({}, context())
            self.assertIsNone(result.changed)
            self.assertNotIn('restore_spooler_stopped', worker.calls)
            record = next(Path(directory).iterdir())
            self.assertEqual(json.loads(record.read_text())['state'], 'pending')

    def test_human_elevation_required(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = Worker([{'status': 'Stopped'}, NativeError('elevation_required')])
            result = WindowsExecutor(worker, Path(directory)).start_spooler({}, context())
            self.assertEqual(result.status, 'blocked')
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_failed_recovery_retains_record(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = Worker([{'status': 'Stopped'}, {'changed': True}, NativeError('timeout'), NativeError('timeout')])
            result = WindowsExecutor(worker, Path(directory)).start_spooler({}, context())
            self.assertFalse(result.evidence['recovered'])
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_worker_rejects_arbitrary_operation(self):
        with patch('subprocess.run') as run:
            with self.assertRaises(NativeError):
                PowerShellWorker().run('desktop', 'type_shell', {})
            run.assert_not_called()

    def test_worker_payload_is_stdin_not_command(self):
        reply = subprocess.CompletedProcess([], 0, '{"ok":true,"evidence":{}}', '')
        with patch('subprocess.run', return_value=reply) as run:
            PowerShellWorker().run('diagnostics', 'system_snapshot', {'text': '$(malicious)'})
            args, kwargs = run.call_args
            self.assertNotIn('$(malicious)', ' '.join(args[0]))
            self.assertFalse(kwargs['shell'])
            self.assertEqual(json.loads(kwargs['input'])['text'], '$(malicious)')

    def test_worker_rejects_malformed_envelope(self):
        for stdout in ('garbage', '{"ok":true}', '{"ok":true,"evidence":[]}'):
            with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout, '')):
                with self.assertRaises(NativeError):
                    PowerShellWorker().run('diagnostics', 'system_snapshot', {})

    def test_worker_timeout(self):
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('worker', 20)):
            with self.assertRaises(NativeError) as error:
                PowerShellWorker().run('diagnostics', 'system_snapshot', {})
            self.assertEqual(error.exception.code, 'timeout')
