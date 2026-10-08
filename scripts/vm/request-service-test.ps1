$ErrorActionPreference='Stop'
# Windows itself displays UAC; no password or approval input is automated.
$script=Join-Path $PSScriptRoot 'test-spooler-guest.ps1'
Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$script,'-SnapshotId','d92e3823-463e-4b5a-9ea1-dc4312c05450')
