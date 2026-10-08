# Fixed developer-only disposable-guest fault/repair test. Run after human UAC.
param([Parameter(Mandatory=$true)][string]$SnapshotId)
$ErrorActionPreference='Stop'
if($SnapshotId -ne 'd92e3823-463e-4b5a-9ea1-dc4312c05450'){throw 'Known fresh preflight recovery snapshot required'}
$principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Human-approved elevated guest session required'}
$resultPath=Join-Path $PSScriptRoot 'service-test-result.json'
$recordPath=Join-Path $PSScriptRoot 'service-test-recovery.json'
if(Test-Path -LiteralPath $recordPath){throw 'Inspect prior pending recovery before another service test'}
if((Get-Service Spooler).Status -ne 'Running'){throw 'Healthy Running Spooler baseline required'}
$report=@{snapshot_id=$SnapshotId;provider='none';started_at=[DateTime]::UtcNow.ToString('o');before='Running';postcondition_met=$false;restored=$false;actual_print_verified=$false}
@{service='Spooler';original_status='Running';state='pending'}|ConvertTo-Json|Set-Content -LiteralPath $recordPath -Encoding UTF8
try {
    Stop-Service -Name Spooler
    (Get-Service Spooler).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(10))
    $report.fault_status=[string](Get-Service Spooler).Status
    $reader=New-Object IO.StringReader('{"expected_status":"Stopped"}')
    $old=[Console]::In
    try {
        [Console]::SetIn($reader)
        $reply=(& (Join-Path $PSScriptRoot 'diagnostics.ps1') -Operation start_spooler)|ConvertFrom-Json
        if(-not $reply.ok){throw ('Fixed repair refused: '+$reply.code)}
        $report.repair=$reply.evidence
    }finally{[Console]::SetIn($old);$reader.Dispose()}
    (Get-Service Spooler).WaitForStatus('Running',[TimeSpan]::FromSeconds(10))
    $report.after=[string](Get-Service Spooler).Status
    $report.postcondition_met=($report.after -eq 'Running')
}catch {$report.error='service_test_failed'}
finally {
    try {
        if((Get-Service Spooler).Status -ne 'Running'){Start-Service Spooler}
        (Get-Service Spooler).WaitForStatus('Running',[TimeSpan]::FromSeconds(10))
        $report.restored=((Get-Service Spooler).Status -eq 'Running')
        if($report.restored){Remove-Item -LiteralPath $recordPath}
    }catch {$report.recovery_error='recovery_failed_inspect_snapshot'}
    $report.finished_at=[DateTime]::UtcNow.ToString('o')
    $report|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $resultPath -Encoding UTF8
}
