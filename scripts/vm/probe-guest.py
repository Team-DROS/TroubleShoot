"""Fresh read-only guest probe using locally entered, temporary credentials.

Run request-login.ps1 first. This development helper is not a model tool.
It transfers only guest-probe.ps1 and never receives a password on its CLI.
"""
import json
import os
import subprocess
from pathlib import Path


def main():
    auth_file = Path(os.environ['LOCALAPPDATA']) / 'TroubleShootEvent/vm-auth/login.json'
    if not auth_file.exists():
        raise SystemExit('Awaiting local login dialog entry.')
    auth = json.loads(auth_file.read_text(encoding='utf-8-sig'))
    if auth.get('status') != 'ready':
        raise SystemExit('Local login was not completed.')
    password_file = Path(auth['password_file']).resolve()
    if password_file.parent != auth_file.parent.resolve():
        raise SystemExit('Invalid local credential file location.')
    vbox = Path(os.environ['ProgramFiles']) / 'Oracle/VirtualBox/VBoxManage.exe'
    prefix = [str(vbox), 'guestcontrol', 'TROUBLESHOOT-Test']
    credentials = ['--username', auth['username'], '--passwordfile', str(password_file)]
    directory = r'C:\Users\Public\TroubleShootFresh'
    def invoke(operation, arguments):
        result = subprocess.run(prefix + [operation] + credentials + arguments,
                                capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=50, shell=False)
        if result.returncode:
            # Avoid printing command lines or diagnostic text containing account data.
            raise SystemExit(f'Guest {operation} failed (code {result.returncode}); check account locally. No retry attempted.')
        return result.stdout
    try:
        invoke('mkdir', ['--parents', directory])
        invoke('copyto', ['--target-directory', directory, str(Path(__file__).with_name('guest-probe.ps1'))])
        powershell = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        output = invoke('run', ['--exe', powershell, '--timeout', '30000', '--wait-stdout', '--wait-stderr',
                                '--', powershell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                                '-File', directory + r'\guest-probe.ps1'])
        for line in output.splitlines():
            if line.strip().startswith('{'):
                evidence = json.loads(line)
                print(json.dumps(evidence, sort_keys=True))
                break
        else:
            raise SystemExit('Guest produced no structured probe; no live result claimed.')
    finally:
        # Exact validated local file only, never recursive deletion.
        password_file.unlink(missing_ok=True)
        auth_file.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
