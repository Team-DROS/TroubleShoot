import tempfile
import unittest
from pathlib import Path
from troubleshoot.desktop.recovery import CheckboxRecovery
from troubleshoot.windows.policy import ExecutionResult
from test_desktop_executor import snapshot, context


class Fake:
    def __init__(self):
        self.snap = snapshot()
        self.calls = []
        self.fail = False

    def observe(self, target):
        return self.snap

    def toggle_checkbox(self, snap, args, ctx):
        self.calls.append(args)
        if ctx.consume_authorization is None:
            return ExecutionResult('blocked', {})
        if self.fail:
            return ExecutionResult('failed', {}, None)
        self.snap.metadata['controls'][0]['toggle_state'] = args['state']
        return ExecutionResult('ok', {'postcondition_met': True}, True)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.executor = Fake()
        self.recovery = CheckboxRecovery(self.executor, Path(self.temp.name))

    def apply(self):
        return self.recovery.apply(self.executor.snap, {'control_id': 'control', 'state': 'On'}, context())

    def test_durable_restore_and_delete_only_after_verified(self):
        result = self.apply()
        self.assertTrue(list(Path(self.temp.name).glob('*.json')))
        restored = self.recovery.restore(result.evidence['recovery_id'], context())
        self.assertTrue(restored.evidence['baseline_restored'])
        self.assertEqual(self.executor.calls[-1]['state'], 'Off')
        self.assertFalse(list(Path(self.temp.name).glob('*.json')))

    def test_uncertain_action_retains_record(self):
        self.executor.fail = True
        self.assertEqual(self.apply().status, 'failed')
        self.assertTrue(list(Path(self.temp.name).glob('*.json')))

    def test_pending_record_blocks_next_mutation(self):
        self.apply()
        self.assertEqual(self.apply().status, 'ok')  # already desired; no additional mutation
        self.executor.snap.metadata['controls'][0]['toggle_state'] = 'Off'
        self.assertEqual(self.apply().status, 'blocked')

    def test_replacement_control_blocks_recovery(self):
        result = self.apply()
        self.executor.snap.metadata['controls'][0]['name'] = 'Replacement'
        self.assertEqual(self.recovery.restore(result.evidence['recovery_id'], context()).status, 'blocked')
        self.assertTrue(list(Path(self.temp.name).glob('*.json')))

    def test_recovery_needs_approval(self):
        result = self.apply()
        self.assertEqual(self.recovery.restore(result.evidence['recovery_id'], context(approval=None)).status, 'blocked')
        self.assertTrue(list(Path(self.temp.name).glob('*.json')))

    def test_already_restored_needs_no_input(self):
        result = self.apply()
        self.executor.snap.metadata['controls'][0]['toggle_state'] = 'Off'
        before = len(self.executor.calls)
        self.assertTrue(self.recovery.restore(result.evidence['recovery_id'], context()).evidence['already_restored'])
        self.assertEqual(len(self.executor.calls), before)

    def test_intervening_indeterminate_state_never_overwritten(self):
        result = self.apply()
        self.executor.snap.metadata['controls'][0]['toggle_state'] = 'Indeterminate'
        before = len(self.executor.calls)
        self.assertEqual(self.recovery.restore(result.evidence['recovery_id'], context()).status, 'blocked')
        self.assertEqual(len(self.executor.calls), before)

    def test_persistence_failure_prevents_input(self):
        path = Path(self.temp.name) / 'not-a-directory'
        path.write_text('occupied')
        recovery = CheckboxRecovery(self.executor, path)
        result = recovery.apply(self.executor.snap, {'control_id': 'control', 'state': 'On'}, context())
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(self.executor.calls, [])
