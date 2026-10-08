param([ValidateSet('prepare','apply')][string]$Stage)
$ErrorActionPreference='Stop'
if($env:TROUBLESHOOT_VM_TEST -ne '1'){throw 'Disposable guest marker required'}
$stateFile=Join-Path $PSScriptRoot 'gemma-desktop-state.json'
$captureFile=Join-Path $PSScriptRoot 'gemma-desktop-capture.json'
function Native($op,$payload){
    $old=[Console]::In;$reader=New-Object IO.StringReader(($payload|ConvertTo-Json -Depth 16 -Compress))
    try{[Console]::SetIn($reader);$r=((& (Join-Path $PSScriptRoot 'worker.ps1') -Operation $op)-join "`n")|ConvertFrom-Json;if(-not $r.ok){throw $r.code};$r.evidence}
    finally{[Console]::SetIn($old);$reader.Dispose()}
}
if($Stage -eq 'prepare'){
    if(Test-Path $stateFile){throw 'Inspect prior fixture state before another test'}
    $directory=Join-Path $PSScriptRoot ('GemmaFixture-'+[guid]::NewGuid().ToString('N'))
    $exe=& (Join-Path $PSScriptRoot 'build-fixture.ps1') -OutputDirectory $directory
    $fixture=Start-Process $exe -WindowStyle Normal -PassThru
    Start-Sleep -Seconds 3
    $target=@((Native 'list_targets' @{}).targets|Where-Object {$_.target.pid -eq $fixture.Id})[0].target
    $snapshot=Native 'observe' @{target=$target}
    $capture=Native 'capture' @{snapshot=$snapshot;capture_consent=$true}
    @{snapshot=$snapshot;png_base64=$capture.png_base64}|ConvertTo-Json -Depth 16|Set-Content $captureFile -Encoding UTF8
    @{target=$target;exe=$exe;before='Off'}|ConvertTo-Json -Depth 6|Set-Content $stateFile -Encoding UTF8
    @{prepared=$true;synthetic_ui=$true}|ConvertTo-Json -Compress
    exit
}
$saved=Get-Content $stateFile -Raw|ConvertFrom-Json
$proposal=Get-Content (Join-Path $PSScriptRoot 'gemma-desktop-proposal.json') -Raw|ConvertFrom-Json
if($proposal.operation -ne 'toggle_checkbox' -or $proposal.state -ne 'On' -or $proposal.name -ne 'Enable demonstration feature'){throw 'Out-of-scope model proposal'}
Add-Type -AssemblyName System.Windows.Forms
$report=@{provider='ollama';model='gemma4:e2b';synthetic_ui=$true;symptom_verified=$false;approved=$false;fixture_state_verified=$false;restored=$false;observed_at=[DateTime]::UtcNow.ToString('o')}
try{
    # Explicit human approval of this exact checkbox and baseline restoration; no UAC automation.
    $answer=[Windows.Forms.MessageBox]::Show('Real Gemma proposed enabling the synthetic demonstration feature. Approve setting only this checkbox to On, verifying it, then restoring its original Off state? No real Windows repair is claimed.','TroubleShoot: approve Gemma VM test','YesNo','Question')
    if($answer -ne 'Yes'){throw 'human_denied'}
    $report.approved=$true
    # Human approval is followed by fresh native binding; baseline/identity must still agree.
    Start-Sleep -Milliseconds 200
    $snapshot=Native 'observe' @{target=$saved.target}
    $control=@($snapshot.controls|Where-Object {$_.control_id -eq $proposal.control_id -and $_.name -eq $proposal.name -and $_.type -eq 'CheckBox'})
    if($control.Count -ne 1 -or $control[0].toggle_state -ne 'Off'){throw 'baseline_changed'}
    $applied=Native 'toggle_checkbox' @{snapshot=$snapshot;control=$control[0];desired_state='On'}
    $after=Native 'observe' @{target=$saved.target}
    $report.fixture_state_verified=($applied.postcondition_met -and @($after.controls|Where-Object {$_.name -eq 'Feature state: True'}).Count -eq 1)
    $report.before='Off';$report.after=@($after.controls|Where-Object {$_.control_id -eq $proposal.control_id})[0].toggle_state
    $restoreSnapshot=Native 'observe' @{target=$saved.target}
    $restoreControl=@($restoreSnapshot.controls|Where-Object {$_.control_id -eq $proposal.control_id})[0]
    if($restoreControl.toggle_state -ne 'On'){throw 'recovery_state_changed'}
    $restored=Native 'toggle_checkbox' @{snapshot=$restoreSnapshot;control=$restoreControl;desired_state='Off'}
    $check=Native 'observe' @{target=$saved.target}
    $report.restored=($restored.postcondition_met -and @($check.controls|Where-Object {$_.control_id -eq $proposal.control_id -and $_.toggle_state -eq 'Off'}).Count -eq 1)
}catch{$report.error=$_.Exception.Message}
finally{
    [IO.File]::WriteAllText(($saved.exe+'.cleanup'),'cleanup')
    Start-Sleep -Seconds 1
    $report.fixture_closed=(@(Get-Process TroubleShootFixture -ErrorAction SilentlyContinue|Where-Object {$_.Id -eq $saved.target.pid}).Count -eq 0)
    $report|ConvertTo-Json -Depth 8|Set-Content (Join-Path $PSScriptRoot 'gemma-desktop-result.json') -Encoding UTF8
    if($report.fixture_closed){Remove-Item $stateFile}
}
$report|ConvertTo-Json -Depth 8 -Compress
