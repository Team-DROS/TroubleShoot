$ErrorActionPreference='Stop'
if($env:TROUBLESHOOT_VM_TEST -ne '1'){throw 'Guest test marker required'}
. (Join-Path $PSScriptRoot 'mouse-native.ps1')
. (Join-Path $PSScriptRoot 'mouse-test-keys.ps1')
$before=@{busy=[TSMouse]::Busy();escape=[TSMouse]::Escape()}
[TSMouseTestKeys]::ReleaseEscape();[TSMouseTestKeys]::ReleaseControl();Start-Sleep -Milliseconds 50
$remaining=@(Get-Process -Name TroubleShootFixture -ErrorAction SilentlyContinue|Where-Object {$_.Path.StartsWith($PSScriptRoot+'\MouseFixture-',[StringComparison]::OrdinalIgnoreCase)})
@{before=$before;busy_after=[TSMouse]::Busy();escape_after=[TSMouse]::Escape();fresh_mouse_fixtures_remaining=$remaining.Count}|ConvertTo-Json -Compress
