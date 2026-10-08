"""Durable recovery for one checkbox; never infer a generic undo from mouse input."""
import json
import os
import uuid
from dataclasses import asdict
from pathlib import Path

from troubleshoot.contracts import ContractError, Target
from troubleshoot.windows.policy import ExecutionResult
from troubleshoot.windows.runner import NativeError
from .executor import toggle_arguments


class CheckboxRecovery:
    def __init__(self, executor, directory: Path):
        self.executor = executor
        self.directory = Path(directory)

    def _save(self, path, record):
        temporary = path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(record, stream, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def apply(self, snapshot, arguments, context):
        arguments = toggle_arguments(arguments)
        controls = [c for c in snapshot.metadata['controls'] if c['control_id'] == arguments['control_id']]
        if len(controls) != 1 or controls[0].get('type') != 'CheckBox' or controls[0].get('toggle_state') not in {'On', 'Off'}:
            return ExecutionResult('blocked', {'reason': 'Recoverable checkbox baseline required'})
        control = controls[0]
        if control['toggle_state'] == arguments['state']:
            return self.executor.toggle_checkbox(snapshot, arguments, context)
        record = {'target': asdict(snapshot.observation.target), 'control_id': control['control_id'],
                  'name': control['name'], 'type': control['type'], 'before': control['toggle_state'],
                  'expected_after': arguments['state'], 'run_id': context.run_id, 'state': 'pending'}
        path = self.directory / (uuid.uuid4().hex + '.json')
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            # Pending records require inspection before another workflow mutation.
            if any(self.directory.glob('*.json')):
                return ExecutionResult('blocked', {'reason': 'Inspect pending desktop recovery first'})
            self._save(path, record)
        except OSError:
            return ExecutionResult('blocked', {'reason': 'Recovery persistence failed; no input sent'})
        result = self.executor.toggle_checkbox(snapshot, arguments, context)
        if result.status == 'blocked':
            path.unlink()
            return result
        return ExecutionResult(result.status, {**result.evidence, 'recovery_id': path.stem},
                               result.changed, result.limitations + ('Retain baseline until symptom verification; restore requires new approval.',))

    def restore(self, recovery_id, context):
        if not isinstance(recovery_id, str) or len(recovery_id) != 32 or any(c not in '0123456789abcdef' for c in recovery_id):
            raise ContractError('Invalid recovery ID')
        path = self.directory / (recovery_id + '.json')
        try:
            record = json.loads(path.read_text(encoding='utf-8'))
            if record['before'] not in {'On', 'Off'} or record['expected_after'] not in {'On', 'Off'} or record['type'] != 'CheckBox':
                raise ContractError('Invalid baseline record')
            current = self.executor.observe(Target.from_dict(record['target']))
            matches = [c for c in current.metadata['controls'] if c['control_id'] == record['control_id']]
            if len(matches) != 1 or matches[0]['name'] != record['name'] or matches[0]['type'] != 'CheckBox':
                return ExecutionResult('blocked', {'reason': 'Recovery target/control changed'})
            state = matches[0].get('toggle_state')
            if state == record['before']:
                path.unlink()
                return ExecutionResult('ok', {'baseline_restored': True, 'already_restored': True})
            if state != record['expected_after']:
                return ExecutionResult('blocked', {'reason': 'Intervening checkbox change; inspect manually'})
            result = self.executor.toggle_checkbox(current, {'control_id': record['control_id'], 'state': record['before']}, context)
            if result.status == 'ok' and result.evidence.get('postcondition_met') is True:
                path.unlink()
                return ExecutionResult('ok', {**result.evidence, 'baseline_restored': True}, result.changed)
            return result
        except (OSError, ValueError, KeyError, ContractError, NativeError):
            return ExecutionResult('blocked', {'reason': 'Recovery inspection failed; retain record and inspect manually'})
