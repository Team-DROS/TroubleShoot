# Developer-only fresh VM harness. No credential, image or arbitrary UI text in evidence.
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$desktop=Join-Path $root 'worker.ps1'
$diagnostics=Join-Path $root 'diagnostics.ps1'
$checks=New-Object Collections.Generic.List[object]
function Invoke-Worker($script,$operation,$payload) {
    $old=[Console]::In
    $reader=New-Object IO.StringReader(($payload|ConvertTo-Json -Depth 16 -Compress))
    try {
        [Console]::SetIn($reader)
        $raw=& $script -Operation $operation
        $reply=($raw -join "`n")|ConvertFrom-Json
        if(-not $reply.ok){throw ('Worker refused: '+$reply.code)}
        return $reply.evidence
    }finally{[Console]::SetIn($old);$reader.Dispose()}
}
function Expect-Rejection($case,$operation,$payload,$expectedCode) {
    $old=[Console]::In
    $reader=New-Object IO.StringReader(($payload|ConvertTo-Json -Depth 16 -Compress))
    try {
        [Console]::SetIn($reader)
        $reply=((& $desktop -Operation $operation) -join "`n")|ConvertFrom-Json
        $checks.Add(@{case=$case;passed=($reply.ok -eq $false -and $reply.code -eq $expectedCode);code=$reply.code})
    }finally{[Console]::SetIn($old);$reader.Dispose()}
}
$os=Invoke-Worker $diagnostics 'system_snapshot' @{}
$spooler=Invoke-Worker $diagnostics 'spooler_status' @{}
$checks.Add(@{case='healthy_diagnosis';passed=($spooler.status -eq 'Running');service_status=$spooler.status})
$directory=Join-Path $root ('Fixture-'+[guid]::NewGuid().ToString('N'))
$exe=& (Join-Path $root 'build-fixture.ps1') -OutputDirectory $directory
$fixture=Start-Process -FilePath $exe -WindowStyle Normal -PassThru
try {
    Start-Sleep -Seconds 3
    $list=Invoke-Worker $desktop 'list_targets' @{}
    $selected=@($list.targets|Where-Object {$_.target.pid -eq $fixture.Id})
    if($selected.Count -ne 1){
        $fixture.Refresh()
        @{case='fixture_not_enumerated';main_window_handle=$fixture.MainWindowHandle.ToInt64();session_id=$fixture.SessionId;enumerated_count=$list.targets.Count}|ConvertTo-Json -Compress|Write-Output
        throw 'Fixture did not appear in the interactive desktop'
    }
    $target=$selected[0].target
    $before=Invoke-Worker $desktop 'observe' @{target=$target}
    Expect-Rejection 'capture_denied' 'capture' @{snapshot=$before;capture_consent=$false} 'capture_consent_required'
    $stale=($before|ConvertTo-Json -Depth 16|ConvertFrom-Json)
    $stale.observed_at=[DateTime]::UtcNow.AddSeconds(-10).ToString('o')
    Expect-Rejection 'stale_capture' 'capture' @{snapshot=$stale;capture_consent=$true} 'stale_observation'
    $wrong=@{handle=$target.handle;pid=($target.pid+1);started=$target.started}
    Expect-Rejection 'reused_identity' 'observe' @{target=$wrong} 'target_changed'
    $before=Invoke-Worker $desktop 'observe' @{target=$target}
    $feature=@($before.controls|Where-Object {$_.name -eq 'Enable demonstration feature' -and $_.type -eq 'CheckBox'})[0]
    # Human has authorized fixture input via VM-validation request. This tests native
    # mechanics; Python policy/approval gates are independently unit tested.
    $toggle=Invoke-Worker $desktop 'toggle_checkbox' @{snapshot=$before;control=$feature;desired_state='On'}
    $checks.Add(@{case='synthetic_checkbox';passed=$toggle.postcondition_met;original_symptom_verified=$false})
    $before=Invoke-Worker $desktop 'observe' @{target=$target}
    $capture=Invoke-Worker $desktop 'capture' @{snapshot=$before;capture_consent=$true}
    $bytes=[Convert]::FromBase64String($capture.png_base64)
    $checks.Add(@{case='selected_window_capture';passed=($bytes.Length -gt 8);byte_count=$bytes.Length;image_retained=$false})
    $before=Invoke-Worker $desktop 'observe' @{target=$target}
    $closed=Invoke-Worker $desktop 'graceful_close' @{snapshot=$before}
    $checks.Add(@{case='save_confirmation_partial';passed=(-not $closed.postcondition_met -and $closed.remaining_process_windows -ge 1);remaining_windows=$closed.remaining_process_windows})
    $blocked=Invoke-Worker $desktop 'observe' @{target=$target}
    Expect-Rejection 'foreground_loss' 'graceful_close' @{snapshot=$blocked} 'foreground_changed'
} finally {
    # Fixture-only cooperative cleanup; never kill another process or real application.
    [IO.File]::WriteAllText($exe+'.cleanup','cleanup')
    $fixture.WaitForExit(5000)|Out-Null
    $checks.Add(@{case='fixture_cooperative_recovery';passed=$fixture.HasExited})
}
@{checks=$checks.ToArray();os=$os;provider='none';synthetic_ui=$true;service_fault_attempted=$false}|ConvertTo-Json -Depth 16 -Compress
