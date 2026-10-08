# Short visible developer demo in the guest only; predetermined native actions, no model claim.
$ErrorActionPreference='Stop'
if($env:TROUBLESHOOT_VM_TEST -ne '1'){throw 'Run only in the marked disposable guest session'}
$env:TROUBLESHOOT_DEMO='1'
$worker=Join-Path $PSScriptRoot 'worker.ps1'
function Invoke-Json($op,$payload){
    $old=[Console]::In;$reader=New-Object IO.StringReader(($payload|ConvertTo-Json -Depth 16 -Compress))
    try {[Console]::SetIn($reader);$r=((& $worker -Operation $op) -join "`n")|ConvertFrom-Json;if(-not $r.ok){throw ('Demo stopped: '+$r.code)};return $r.evidence}
    finally{[Console]::SetIn($old);$reader.Dispose()}
}
function Stage($text){[IO.File]::WriteAllText((Join-Path $directory 'demo-stage.txt'),$text);Start-Sleep -Milliseconds 900}
function Action($op,$name,$extra=@{}){
    $before=Invoke-Json 'observe' @{target=$script:target}
    $control=@($before.controls|Where-Object {$_.name -eq $name -and $_.type -ne 'Text'})[0]
    if($null -eq $control){throw ('Demo control missing: '+$name)}
    $args=@{control_id=$control.control_id;x=[int]($control.bounds.left+$control.bounds.width/2-$before.bounds.left);y=[int]($control.bounds.top+$control.bounds.height/2-$before.bounds.top)}
    foreach($key in $extra.Keys){$args[$key]=$extra[$key]}
    Invoke-Json $op @{snapshot=$before;control=$control;arguments=$args}
}
$directory=Join-Path $PSScriptRoot ('MouseDemo-'+[guid]::NewGuid().ToString('N'))
$exe=& (Join-Path $PSScriptRoot 'build-mouse-fixture.ps1') -OutputDirectory $directory
$fixture=Start-Process -FilePath $exe -WindowStyle Normal -PassThru
try {
    Start-Sleep -Seconds 3
    $list=Invoke-Json 'list_targets' @{}
    $script:target=@($list.targets|Where-Object {$_.target.pid -eq $fixture.Id})[0].target
    if($null -eq $script:target){throw 'Demo window not available'}
    Stage '1/4   Observe the selected app, then move the cursor'
    $r=Action 'mouse_move' 'Count clicks'
    Stage '2/4   Click the selected button — verify the counter'
    $r=Action 'mouse_click' 'Count clicks'
    Stage '3/4   Scroll the selected list — verify its position'
    $r=Action 'mouse_scroll' 'Test scroll list' @{ticks=-2}
    Stage '4/4   Drag the slider — verify its new value'
    $before=Invoke-Json 'observe' @{target=$script:target}
    $slider=@($before.controls|Where-Object {$_.name -eq 'Test slider' -and $_.type -eq 'Slider'})[0]
    $thumb=@($before.controls|Where-Object {$_.type -eq 'Thumb' -and $_.bounds.left -ge $slider.bounds.left -and $_.bounds.left -lt ($slider.bounds.left+$slider.bounds.width)})
    if($thumb.Count -ne 1){throw 'Demo slider thumb not uniquely available'}
    $args=@{control_id=$slider.control_id;x=[int]($thumb[0].bounds.left+$thumb[0].bounds.width/2-$before.bounds.left);
        y=[int]($thumb[0].bounds.top+$thumb[0].bounds.height/2-$before.bounds.top);
        to_x=[int]($slider.bounds.left+$slider.bounds.width*.75-$before.bounds.left);to_y=[int]($slider.bounds.top+$slider.bounds.height/2-$before.bounds.top)}
    $r=Invoke-Json 'mouse_drag' @{snapshot=$before;control=$slider;arguments=$args}
    $after=Invoke-Json 'observe' @{target=$script:target}
    $names=@($after.controls|ForEach-Object {$_.name})
    $verified=('Clicks: 1' -in $names -and @($names|Where-Object {$_ -like 'Scroll offset:*' -and $_ -ne 'Scroll offset: 0'}).Count -eq 1 -and @($names|Where-Object {$_ -like 'Slider:*' -and [int]($_.Replace('Slider: ','')) -ge 60}).Count -eq 1)
    if(-not $verified){throw 'Demo postcondition not met'}
    Stage 'VERIFIED   Click count, scroll position and slider value changed'
    @{demo_complete=$true;fixture_state_verified=$true;provider='none';symptom_verified=$false}|ConvertTo-Json -Compress
    # Keep the genuine final state visible for recording; user can close this synthetic app.
} catch {
    Stage 'STOPPED   A safety check or verification failed — no automatic retry'
    throw
}
