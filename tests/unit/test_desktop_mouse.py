import copy
import subprocess
import unittest
from datetime import datetime, timezone
from threading import Event
from unittest.mock import patch

from troubleshoot.contracts import ContractError, Observation, Target
from troubleshoot.desktop.executor import DesktopExecutor, WindowObservation
from troubleshoot.desktop.mouse import MOUSE_VALIDATORS, image_to_window
from troubleshoot.windows.policy import ExecutionContext
from troubleshoot.windows.runner import NativeError, PowerShellWorker

NOW = datetime(2026, 10, 8, 7, tzinfo=timezone.utc)
TARGET = Target(42, 100, '2026-10-08T06:00:00Z')


def snapshot():
    return WindowObservation(Observation('obs', NOW.isoformat(), TARGET), {
        'target': {'handle': 42, 'pid': 100, 'started': TARGET.started}, 'observed_at': NOW.isoformat(),
        'bounds': {'left': -300, 'top': 20, 'width': 200, 'height': 150},
        'client_bounds': {'left': -290, 'top': 40, 'width': 180, 'height': 120},
        'virtual_screen': [-1920, 0, 3840, 1080], 'cursor': [-280, 60], 'dpi': 144, 'foreground': True,
        'controls': [{'control_id': 'button', 'name': 'Count clicks', 'type': 'Button', 'enabled': True,
                      'offscreen': False, 'bounds': {'left': -280, 'top': 50, 'width': 100, 'height': 50}}],
    })


class Worker:
    def __init__(self, metadata=None, reply=None):
        self.metadata = metadata or snapshot().metadata
        self.reply = reply or {'input_delivered': True, 'symptom_verified': False}
        self.calls = []

    def run(self, worker, operation, payload):
        self.calls.append(operation)
        return self.metadata

    def run_cancellable(self, worker, operation, payload, cancelled):
        self.calls.append(operation)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def context(mode='repair', approve=lambda request: True):
    return ExecutionContext('run', 'action', mode, Event(), approve)


class MouseTests(unittest.TestCase):
    def action(self, worker=None, snap=None, args=None, ctx=None, operation='mouse_click'):
        return DesktopExecutor(worker or Worker(), lambda: NOW).mouse_action(
            operation, snap or snapshot(), args or {'control_id': 'button', 'x': 30, 'y': 40}, ctx or context())

    def test_integer_only_coordinates(self):
        for value in (True, 1.5, '30', -1, 32768, None):
            with self.assertRaises(ContractError):
                self.action(args={'control_id': 'button', 'x': value, 'y': 40})

    def test_unknown_actions_buttons_and_extra_fields(self):
        with self.assertRaises(ContractError):
            self.action(operation='type_shell')
        with self.assertRaises(ContractError):
            self.action(args={'control_id': 'button', 'x': 30, 'y': 40, 'button': 'right'})

    def test_scroll_is_bounded_integer_not_zero(self):
        for ticks in (True, 0, 6, -6, '1'):
            with self.assertRaises(ContractError):
                MOUSE_VALIDATORS['mouse_scroll']({'control_id': 'list', 'x': 30, 'y': 40, 'ticks': ticks})

    def test_drag_endpoint_and_no_duration_override(self):
        for extra in ({'to_x': 30, 'to_y': 40}, {'to_x': 40, 'to_y': 50, 'duration_ms': 10000}):
            with self.assertRaises(ContractError):
                MOUSE_VALIDATORS['mouse_drag']({'control_id': 'slider', 'x': 30, 'y': 40, **extra})

    def test_image_mapping_scaling_and_negative_monitor_origin(self):
        self.assertEqual(image_to_window(0, 0, 100, 75, snapshot()), {'x': 1, 'y': 1})
        self.assertEqual(image_to_window(99, 74, 100, 75, snapshot()), {'x': 199, 'y': 149})
        self.assertEqual(image_to_window(30, 40, 200, 150, snapshot()), {'x': 30, 'y': 40})

    def test_image_mapping_rejects_invalid_dimensions(self):
        for width, x in ((0, 0), (True, 0), (100, 100), (100, -1)):
            with self.assertRaises(ContractError):
                image_to_window(x, 0, width, 75, snapshot())

    def test_outside_window_client_and_control(self):
        for x, y in ((200, 40), (5, 5), (150, 40), (30, 149)):
            worker = Worker()
            self.assertEqual(self.action(worker, args={'control_id': 'button', 'x': x, 'y': y}).status, 'blocked')
            self.assertEqual(worker.calls, ['observe'])

    def test_geometry_monitor_cursor_and_foreground_rejection(self):
        changes = {'dpi': 96, 'cursor': [-279, 60], 'virtual_screen': [0, 0, 1920, 1080],
                   'client_bounds': {'left': 0}, 'foreground': False}
        for key, value in changes.items():
            current = copy.deepcopy(snapshot().metadata); current[key] = value
            worker = Worker(current)
            self.assertEqual(self.action(worker).status, 'blocked')
            self.assertEqual(worker.calls, ['observe'])

    def test_replaced_pid_start_and_stale_identity(self):
        for key, value in (('pid', 101), ('started', '2026-10-08T06:01:00Z')):
            current = copy.deepcopy(snapshot().metadata); current['target'][key] = value
            self.assertEqual(self.action(Worker(current)).status, 'blocked')
        snap = snapshot()
        snap = WindowObservation(Observation('obs', '2026-10-08T06:59:54Z', TARGET), snap.metadata)
        self.assertEqual(self.action(snap=snap).status, 'blocked')

    def test_denied_diagnose_cancelled(self):
        ctx = context(); ctx.cancelled.set()
        for ctx in (context('diagnose'), context(approve=None), context(approve=lambda request: False), ctx):
            worker = Worker()
            self.assertEqual(self.action(worker, ctx=ctx).status, 'blocked')
            self.assertNotIn('mouse_click', worker.calls)

    def test_control_changed_disabled_or_secret(self):
        for key, value in (('name', 'Other'), ('enabled', False), ('offscreen', True), ('type', 'Edit')):
            snap = snapshot(); snap.metadata['controls'][0][key] = value
            worker = Worker(copy.deepcopy(snap.metadata))
            if key == 'name':
                worker.metadata['controls'][0]['name'] = 'Changed again'
            self.assertEqual(self.action(worker, snap=snap).status, 'blocked')

    def test_delivery_is_partial_and_never_claims_symptom_fixed(self):
        result = self.action()
        self.assertEqual(result.status, 'partial')
        self.assertFalse(result.evidence['symptom_verified'])
        self.assertIsNone(result.changed)

    def test_emergency_stop_cancel_and_timeout(self):
        for code, status in (('emergency_stop', 'cancelled'), ('mouse_input_cancelled', 'cancelled'), ('timeout', 'failed')):
            result = self.action(Worker(reply=NativeError(code)))
            self.assertEqual(result.status, status)
            self.assertIsNone(result.changed)

    def test_cancel_while_in_worker(self):
        ctx = context()
        class Cancels(Worker):
            def run_cancellable(self, *args):
                ctx.cancelled.set()
                return {'input_delivered': True}
        self.assertEqual(self.action(Cancels(), ctx=ctx).status, 'cancelled')

    def test_cancelled_transport_never_launches(self):
        cancelled = Event(); cancelled.set()
        with patch('subprocess.Popen') as launch:
            with self.assertRaises(NativeError):
                PowerShellWorker().run_cancellable('desktop', 'mouse_click', {}, cancelled)
            launch.assert_not_called()

    def test_transport_timeout_reaps_worker(self):
        class FakeProcess:
            returncode = None
            killed = False
            def communicate(self, **kwargs):
                if self.killed:
                    return '', ''
                raise subprocess.TimeoutExpired('worker', .05)
            def kill(self):
                self.killed = True; self.returncode = -1
            def poll(self):
                return self.returncode
        process = FakeProcess()
        with patch('subprocess.Popen', return_value=process), patch('time.monotonic', side_effect=[0, 100]):
            with self.assertRaises(NativeError) as error:
                PowerShellWorker().run_cancellable('desktop', 'mouse_move', {}, Event())
            self.assertEqual(error.exception.code, 'timeout')
            self.assertTrue(process.killed)

    def test_cancellation_transport_creates_private_marker(self):
        import json
        from pathlib import Path
        cancelled = Event()
        class FakeProcess:
            returncode = 0
            calls = 0
            def communicate(self, **kwargs):
                self.calls += 1
                if self.calls == 1:
                    cancelled.set()
                    raise subprocess.TimeoutExpired('worker', .05)
                self_marker = Path(wire['cancel_file'])
                self_test.assertTrue(self_marker.exists())
                return '{"ok":true,"evidence":{"cancelled":true}}', ''
            def poll(self):
                return 0
        wire = {}; self_test = self
        def launch(command, **kwargs):
            wire.update(json.loads(kwargs['stdin'].read()))
            self.assertFalse(kwargs['shell'])
            self.assertNotIn(wire['cancel_file'], command)
            return FakeProcess()
        with patch('subprocess.Popen', side_effect=launch):
            result = PowerShellWorker().run_cancellable('desktop', 'mouse_move', {'cancel_file': 'untrusted'}, cancelled)
        self.assertTrue(result['cancelled'])
        self.assertNotEqual(wire['cancel_file'], 'untrusted')
        self.assertFalse(Path(wire['cancel_file']).parent.exists())

    def test_approval_delay_requires_new_observation(self):
        from datetime import timedelta
        now = [NOW]
        def approve(request):
            now[0] += timedelta(seconds=6)
            return True
        worker = Worker()
        result = DesktopExecutor(worker, lambda: now[0]).mouse_action('mouse_click', snapshot(),
            {'control_id': 'button', 'x': 30, 'y': 40}, context(approve=approve))
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(worker.calls, ['observe'])

    def test_drag_destination_must_stay_in_same_control(self):
        snap = snapshot();snap.metadata['controls'][0]['type'] = 'Slider'
        worker = Worker(copy.deepcopy(snap.metadata))
        result = self.action(worker, snap=snap, operation='mouse_drag',
            args={'control_id': 'button', 'x': 30, 'y': 40, 'to_x': 150, 'to_y': 40})
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(worker.calls, ['observe'])
