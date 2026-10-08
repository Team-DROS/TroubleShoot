# Fixed transport for Member 1's unchanged packaged workers. No caller supplies code or paths.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
$wireInput = [Console]::In
$scripts = @{
    diagnostics = Join-Path $PSScriptRoot '../windows/diagnostics.ps1'
    desktop = Join-Path $PSScriptRoot '../desktop/worker.ps1'
}
$allowed = @{
    diagnostics = @('system_snapshot','network_snapshot','spooler_status','start_spooler','restore_spooler_stopped')
    desktop = @('list_targets','observe','capture','toggle_checkbox','graceful_close')
}
$space = [Management.Automation.Runspaces.RunspaceFactory]::CreateRunspace()
$space.Open()
try {
    while ($null -ne ($line = $wireInput.ReadLine())) {
        $pipeline = $null
        $payloadInput = $null
        try {
            if ($line.Length -gt 1000000) { throw 'oversized_request' }
            $request = $line | ConvertFrom-Json
            if ($request.worker -notin @('diagnostics','desktop') -or
                $request.operation -notin $allowed[$request.worker]) { throw 'unregistered_operation' }
            $payloadInput = New-Object IO.StringReader([string]$request.payload)
            [Console]::SetIn($payloadInput)
            $pipeline = [Management.Automation.PowerShell]::Create()
            $pipeline.Runspace = $space
            [void]$pipeline.AddCommand($scripts[$request.worker]).AddParameter('Operation', [string]$request.operation)
            $rows = @($pipeline.Invoke())
            if ($rows.Count -ne 1) { throw 'invalid_output' }
            # The owner worker returns one JSON document even on a policy failure.
            $reply = [string]$rows[0]
            [void]($reply | ConvertFrom-Json)
            [Console]::WriteLine($reply)
        } catch {
            [Console]::WriteLine('{"ok":false,"code":"persistent_worker_failure"}')
        } finally {
            [Console]::SetIn($wireInput)
            if ($pipeline) { $pipeline.Dispose() }
            if ($payloadInput) { $payloadInput.Dispose() }
        }
    }
} finally {
    $space.Dispose()
}
