# Fixed synthetic VM test: mouse mechanics, not real troubleshooting/Gemma reasoning.
$ErrorActionPreference='Stop'
if($env:TROUBLESHOOT_VM_TEST -ne '1'){throw 'Guest test marker required; do not run mouse fault tests on the host'}
. (Join-Path $PSScriptRoot 'mouse-test-keys.ps1')
$worker=Join-Path $PSScriptRoot 'worker.ps1'
$checks=New-Object Collections.Generic.List[object]
function Invoke-Json($op,$payload) {
    $old=[Console]::In;$reader=New-Object IO.StringReader(($payload|ConvertTo-Json -Depth 16 -Compress))
    try {[Console]::SetIn($reader);return ((& $worker -Operation $op) -join "`n")|ConvertFrom-Json}
    finally{[Console]::SetIn($old);$reader.Dispose()}
}
function Observe { $r=Invoke-Json 'observe' @{target=$script:target};if(-not $r.ok){throw ('Observation refused '+$r.code)};return $r.evidence }
function Control($snapshot,$name) {
    $rows=@($snapshot.controls|Where-Object {$_.name -eq $name -and $_.type -ne 'Text'})
    if($rows.Count -ne 1){throw ('Fixture control not unique: '+$name)};return $rows[0]
}
function Point($snapshot,$control) {
    return @{x=[int][Math]::Floor($control.bounds.left+$control.bounds.width/2-$snapshot.bounds.left);
             y=[int][Math]::Floor($control.bounds.top+$control.bounds.height/2-$snapshot.bounds.top)}
}
function Act($op,$name,$extra=@{}) {
    $before=Observe;$control=Control $before $name;$p=Point $before $control
    $args=@{control_id=$control.control_id;x=$p.x;y=$p.y};foreach($k in $extra.Keys){$args[$k]=$extra[$k]}
    $reply=Invoke-Json $op @{snapshot=$before;control=$control;arguments=$args}
    if(-not $reply.ok){throw ('Mouse refused '+$reply.code)}
    return $reply.evidence
}
function Denied($name,$op,$payload,$code) {
    $reply=Invoke-Json $op $payload
    $checks.Add(@{case=$name;passed=($reply.ok -eq $false -and $reply.code -eq $code);code=$reply.code})
}
$directory=Join-Path $PSScriptRoot ('MouseFixture-'+[guid]::NewGuid().ToString('N'))
$exe=& (Join-Path $PSScriptRoot 'build-mouse-fixture.ps1') -OutputDirectory $directory
$fixture=Start-Process -FilePath $exe -WindowStyle Normal -PassThru
$originalCursor=$null
try {
    Start-Sleep -Seconds 3
    $r=Invoke-Json 'list_targets' @{}
    $chosen=@($r.evidence.targets|Where-Object {$_.target.pid -eq $fixture.Id})
    if($chosen.Count -ne 1){throw 'Mouse fixture not on guest desktop'}
    $script:target=$chosen[0].target
    $before=Observe;$originalCursor=$before.cursor
    $moved=Act 'mouse_move' 'Count clicks'
    $checks.Add(@{case='move';passed=$moved.input_delivered})
    $click=Act 'mouse_click' 'Count clicks'
    $checks.Add(@{case='click';passed=(@($click.after.controls|Where-Object {$_.name -eq 'Clicks: 1'}).Count -eq 1)})
    Start-Sleep -Milliseconds 600
    $double=Act 'mouse_double_click' 'Count clicks'
    $doubleNames=@($double.after.controls|Where-Object {$_.name -like 'Double clicks:*'}|ForEach-Object {$_.name})
    $checks.Add(@{case='double_click';passed=($doubleNames.Count -eq 1 -and $doubleNames[0] -eq 'Double clicks: 1');state=$doubleNames})
    $scroll=Act 'mouse_scroll' 'Test scroll list' @{ticks=-2}
    $names=@($scroll.after.controls|Where-Object {$_.name -like 'Scroll offset:*'}|ForEach-Object {$_.name})
    $checks.Add(@{case='scroll';passed=($names.Count -eq 1 -and $names[0] -ne 'Scroll offset: 0');state=$names})
    $before=Observe;$slider=Control $before 'Test slider'
    $thumb=@($before.controls|Where-Object {$_.type -eq 'Thumb' -and $_.bounds.left -ge $slider.bounds.left -and $_.bounds.left -lt ($slider.bounds.left+$slider.bounds.width)})
    $start=if($thumb.Count -eq 1){Point $before $thumb[0]}else{@{x=[int]($slider.bounds.left+$slider.bounds.width*.1-$before.bounds.left);y=[int]($slider.bounds.top+$slider.bounds.height/2-$before.bounds.top)}}
    $args=@{control_id=$slider.control_id;x=$start.x;y=$start.y;to_x=[int]($slider.bounds.left+$slider.bounds.width*.75-$before.bounds.left);to_y=$start.y}
    $drag=Invoke-Json 'mouse_drag' @{snapshot=$before;control=$slider;arguments=$args}
    if(-not $drag.ok){throw ('Drag refused '+$drag.code)}
    $names=@($drag.evidence.after.controls|Where-Object {$_.name -like 'Slider:*'}|ForEach-Object {$_.name})
    $checks.Add(@{case='drag';passed=($names.Count -eq 1 -and [int]($names[0].Replace('Slider: ','')) -ge 60);state=$names})
    $r=Act 'mouse_click' 'Toggle secret overlay';Start-Sleep -Milliseconds 100
    $before=Observe;$button=Control $before 'Count clicks';$p=Point $before $button
    $args=@{control_id=$button.control_id;x=$p.x;y=$p.y}
    Denied 'secret_hit_blocked' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'protected_content'
    $r=Act 'mouse_click' 'Toggle secret overlay';Start-Sleep -Milliseconds 100
    $before=Observe;$button=Control $before 'Count clicks';$p=Point $before $button
    $args=@{control_id=$button.control_id;x=$p.x;y=$p.y}
    [TSMouseTestKeys]::HoldEscape();Start-Sleep -Milliseconds 100
    try {Denied 'escape_stop' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'emergency_stop'}
    finally{[TSMouseTestKeys]::ReleaseEscape()}
    $before=Observe
    [TSMouseTestKeys]::HoldControl();Start-Sleep -Milliseconds 100
    try {Denied 'modifier_interference' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'user_input_active'}
    finally{[TSMouseTestKeys]::ReleaseControl()}
    $before=Observe
    [TSMouseTestKeys]::StartLock()
    try {Denied 'concurrent_input_locked' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'mouse_busy'}
    finally{[TSMouseTestKeys]::StopLock()}
    $r=Act 'mouse_click' 'Toggle cover';Start-Sleep -Milliseconds 100
    $before=Observe
    $r=Act 'mouse_click' 'Arm cancellation'
    $before=Observe;$button=Control $before 'Count clicks';$p=Point $before $button
    $args=@{control_id=$button.control_id;x=$p.x;y=$p.y}
    $midCancel=Join-Path $directory 'cancel-mid'
    Denied 'cancel_between_clicks' 'mouse_double_click' @{snapshot=$before;control=$button;arguments=$args;cancel_file=$midCancel} 'mouse_input_cancelled'
    $after=Observe
    $checks.Add(@{case='cancel_prevents_second_click';passed=(@($after.controls|Where-Object {$_.name -eq 'Clicks: 4'}).Count -eq 1)})
    $before=Observe
    Denied 'covered_point' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'point_occluded'
    $r=Act 'mouse_click' 'Toggle cover';Start-Sleep -Milliseconds 100
    $before=Observe
    $cancel=Join-Path $directory 'cancel';[IO.File]::WriteAllText($cancel,'cancel')
    Denied 'cancel_before_input' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args;cancel_file=$cancel} 'mouse_input_cancelled'
    $before=Observe;$args.x=0;$args.y=0
    Denied 'outside_client' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'point_outside'
    $before=Observe;$args.x=$p.x;$args.y=$p.y;$before.observed_at=[DateTime]::UtcNow.AddSeconds(-10).ToString('o')
    Denied 'stale_mouse' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'stale_observation'
    $before=Observe;$before.target.pid++
    Denied 'replaced_mouse_identity' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'target_changed'
    $before=Observe
    $before.dpi++
    Denied 'changed_dpi' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'geometry_changed'
    $before=Observe;$before.cursor=@(($before.cursor[0]+20),$before.cursor[1])
    Denied 'user_cursor_interference' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'user_cursor_moved'
    $before=Observe;$before.virtual_screen=@(0,0,100,100)
    Denied 'changed_monitor_geometry' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'geometry_changed'
    $before=Observe
    # Fixture-only fault injection via a fixed named accessibility button, avoiding
    # ageing the observation through a second complete mouse observation/action.
    $root=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$script:target.handle)
    $condition=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::NameProperty,'Resize fixture')
    $resize=$root.FindFirst([Windows.Automation.TreeScope]::Descendants,$condition)
    ([Windows.Automation.InvokePattern]$resize.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern)).Invoke()
    Start-Sleep -Milliseconds 50
    Denied 'resized_window' 'mouse_click' @{snapshot=$before;control=$button;arguments=$args} 'geometry_changed'
} finally {
    [TSMouseTestKeys]::ReleaseEscape();[TSMouseTestKeys]::ReleaseControl()
    [TSMouseTestKeys]::StopLock()
    # Cooperative fixture recovery; cursor restoration is fixture-only and explicitly reported.
    [IO.File]::WriteAllText($exe+'.cleanup','cleanup');$fixture.WaitForExit(5000)|Out-Null
    $checks.Add(@{case='fixture_cleanup';passed=$fixture.HasExited})
    if($originalCursor){[TSMouse]::Move($originalCursor[0],$originalCursor[1]);$checks.Add(@{case='cursor_restored';passed=(([TSMouse]::Cursor() -join ',') -eq ($originalCursor -join ','))})}
}
$report=@{observed_at=[DateTime]::UtcNow.ToString('o');provider='none';synthetic_ui=$true;symptom_verified=$false;checks=$checks.ToArray()}
$report|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'mouse-test-result.json') -Encoding UTF8
$report|ConvertTo-Json -Depth 12 -Compress
