# Graceful cleanup confined to freshly built fixture binaries inside this guest folder.
$ErrorActionPreference='Stop'
$prefix=[IO.Path]::GetFullPath($PSScriptRoot)+'\Fixture-'
foreach($process in @(Get-Process -Name TroubleShootFixture -ErrorAction SilentlyContinue)) {
    if(-not $process.Path.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){continue}
    [IO.File]::WriteAllText($process.Path+'.cleanup','cleanup')
    Start-Sleep -Milliseconds 500
    $process.Refresh()
    if(-not $process.HasExited){$process.CloseMainWindow()|Out-Null;$process.WaitForExit(5000)|Out-Null}
    @{fixture_pid=$process.Id;exited=$process.HasExited}|ConvertTo-Json -Compress
}
