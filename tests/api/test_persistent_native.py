"""Real Windows read-only transport checks plus synthetic failure/recovery policy.

No test injects a host fault or performs host desktop input.
"""

import asyncio
import os
import queue
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from troubleshoot.contracts import ActionProposal, Check, ContractError, Observation, Target
from troubleshoot.desktop.executor import WindowObservation
from troubleshoot.desktop.mouse import MOUSE_VALIDATORS
from troubleshoot.runtime.native import NativeExecutorAdapter, native_executor_from_env
from troubleshoot.runtime.ports import RuntimeFailure
from troubleshoot.runtime.powershell_worker import PersistentPowerShellWorker
from troubleshoot.windows.policy import ExecutionResult
from troubleshoot.windows.runner import NativeError


def stamp():
    return datetime.now(timezone.utc).isoformat()


class TransportTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Real PowerShell worker requires Windows")
    def test_readonly_requests_reuse_process_and_failure_has_no_retry(self):
        worker = PersistentPowerShellWorker()
        self.addCleanup(worker.close)
        first = worker.run('diagnostics', 'spooler_status', {})
        pid = worker.process.pid
        second = worker.run('diagnostics', 'spooler_status', {})
        self.assertEqual(worker.process.pid, pid)
        self.assertEqual(first['name'], second['name'])
        self.assertLessEqual((datetime.now(timezone.utc) - datetime.fromisoformat(second['observed_at'])).total_seconds(), 5)
        with self.assertRaises(NativeError):
            worker.run('desktop', 'observe', {'target': {'handle': 9223372036854775807, 'pid': 1, 'started': stamp()}})
        self.assertIsNone(worker.process)  # failed request is discarded, never retried
        self.assertEqual(worker.run('diagnostics', 'spooler_status', {})['name'], first['name'])

    def test_timeout_kills_transport_without_retry(self):
        worker = PersistentPowerShellWorker(timeout=1)
        process = Mock()
        worker.process = process
        worker.replies = Mock()
        worker.replies.get.side_effect = queue.Empty
        with patch.object(worker, '_close') as close, patch.object(worker, '_start') as start:
            with self.assertRaises(NativeError) as raised:
                worker.run('diagnostics', 'start_spooler', {})
        self.assertEqual(raised.exception.code, 'timeout')
        process.stdin.write.assert_called_once()
        close.assert_called_once()
        start.assert_not_called()

    def test_unregistered_input_never_starts_worker(self):
        worker = PersistentPowerShellWorker()
        with patch.object(worker, '_start') as start:
            for operation in ('mouse_click', 'arbitrary_shell'):
                with self.assertRaises(NativeError):
                    worker.run('desktop', operation, {})
            start.assert_not_called()

    @unittest.skipUnless(os.name == 'nt', 'Windows launcher only')
    def test_environment_optin_cannot_enable_repairs_without_symptom_verifier(self):
        with patch.dict(os.environ, {'TROUBLESHOOT_DESKTOP_REPAIRS': '1'}):
            adapter = native_executor_from_env()
        self.assertFalse(adapter.desktop_repairs)
        self.assertEqual(set(adapter.operations_for(Target(2, 2, stamp()))), {'inspect_target'})
        adapter.worker.close()


class SyntheticDesktop:
    def __init__(self, directory):
        self.directory = directory
        self.target = Target(200, 300, stamp())
        self.state = 'Off'
        self.input_count = 0

    def observe(self, target):
        return WindowObservation(Observation('synthetic-' + stamp(), stamp(), self.target), {
            'target': {'handle': self.target.handle, 'pid': self.target.pid, 'started': self.target.started},
            'observed_at': stamp(), 'bounds': {'left': 0, 'top': 0, 'width': 100, 'height': 100},
            'dpi': 96, 'foreground': True,
            'controls': [{'control_id': 'checkbox', 'type': 'CheckBox', 'name': 'Synthetic feature',
                          'toggle_state': self.state, 'enabled': True}]})

    def toggle_checkbox(self, snapshot, arguments, context):
        # Check the actual owner wrapper wrote a baseline before the approval/input boundary.
        assert len(list(self.directory.glob('*.json'))) == 1
        try:
            context.require_mutation('toggle_checkbox', arguments, snapshot.wire(), 'Synthetic checkbox')
        except Exception:
            return ExecutionResult('blocked', {}, False)
        self.state = arguments['state']
        self.input_count += 1
        return ExecutionResult('ok', {'postcondition_met': True}, True)


class RecoveryIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_verified_checkbox_workflow_never_offers_or_dispatches_mouse_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            desktop = SyntheticDesktop(Path(directory))

            async def symptom(action, complaint):
                return [Check('SYNTHETIC symptom', 'On', desktop.state, desktop.state == 'On', stamp())]

            adapter = NativeExecutorAdapter(desktop=desktop, recovery_dir=directory,
                                           desktop_repairs=True, symptom_verifier=symptom)
            self.assertTrue(adapter.desktop_repairs)
            self.assertEqual(set(adapter.operations_for(desktop.target)), {'inspect_target', 'toggle_checkbox'})
            observation = (await adapter.observe(desktop.target)).observation
            authorize = AsyncMock(return_value=True)
            for operation in MOUSE_VALIDATORS:
                with self.subTest(operation=operation):
                    self.assertNotIn(operation, adapter.operations)
                    self.assertNotIn(operation, adapter.status()['operations'])
                    action = ActionProposal('unsupported-mouse', operation, {}, desktop.target,
                                            observation.observation_id)
                    with self.assertRaises(ContractError):
                        await adapter.execute_authorized(action, observation, 'repair', asyncio.Event(), 'run', authorize)
            authorize.assert_not_called()
            self.assertEqual(desktop.input_count, 0)
            self.assertFalse(list(Path(directory).glob('*.json')))

    async def test_checkbox_wrapper_retains_baseline_and_startup_blocks_new_repairs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            desktop = SyntheticDesktop(path)

            async def symptom(action, complaint):
                return [Check('SYNTHETIC symptom', 'On', desktop.state, desktop.state == 'On', stamp())]

            adapter = NativeExecutorAdapter(desktop=desktop, recovery_dir=path,
                                           desktop_repairs=True, symptom_verifier=symptom)
            observation = (await adapter.observe(desktop.target)).observation
            action = ActionProposal('checkbox-action', 'toggle_checkbox', {'control_id': 'checkbox', 'state': 'On'},
                                    desktop.target, observation.observation_id)
            requests = []

            async def authorize(request):
                requests.append(request)
                return True  # explicit synthetic approval, never a production approver

            with patch.object(adapter, '_private_recovery_directory'):
                result = await adapter.execute_authorized(action, observation, 'repair', asyncio.Event(), 'run', authorize)
            self.assertEqual(result.recovery, 'pending')
            self.assertEqual(desktop.input_count, 1)
            self.assertEqual(len(requests), 1)
            self.assertEqual(len(list(path.glob('*.json'))), 1)
            restarted = NativeExecutorAdapter(recovery_dir=path)
            with self.assertRaises(RuntimeFailure):
                restarted.require_recovery_ready()
            self.assertTrue((await adapter.verify(action, 'SYNTHETIC complaint'))[-1].passed)

    async def test_desktop_optin_without_verifier_exposes_no_mutation(self):
        adapter = NativeExecutorAdapter(desktop_repairs=True)
        self.assertFalse(adapter.desktop_repairs)
        self.assertEqual(set(adapter.operations_for(Target(2, 3, stamp()))), {'inspect_target'})
