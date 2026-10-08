$ErrorActionPreference='Stop'
$os=Get-CimInstance Win32_OperatingSystem
$principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
@{
    os=$os.Caption;version=$os.Version
    session_id=(Get-Process -Id $PID).SessionId
    elevated=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    spooler_status=[string](Get-Service -Name Spooler).Status
    python_available=[bool](Get-Command python.exe -ErrorAction SilentlyContinue)
}|ConvertTo-Json -Compress
