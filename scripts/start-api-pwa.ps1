param([int]$Port=8765)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
if(-not $env:GEMMA_API_KEY){
 Add-Type -AssemblyName System.Security
 $keyPath=Join-Path $env:LOCALAPPDATA 'TroubleShoot\api-key.dpapi'
 if(-not (Test-Path -LiteralPath $keyPath)){throw 'Run scripts/configure-api.ps1 first.'}
 $clearKey=[Security.Cryptography.ProtectedData]::Unprotect([IO.File]::ReadAllBytes($keyPath),$null,[Security.Cryptography.DataProtectionScope]::CurrentUser)
 try{$env:GEMMA_API_KEY=[Text.Encoding]::UTF8.GetString($clearKey)}finally{[Array]::Clear($clearKey,0,$clearKey.Length)}
}
try{& (Join-Path $projectRoot '.venv\Scripts\python.exe') -m troubleshoot.api --port $Port --open}finally{Remove-Item Env:GEMMA_API_KEY -ErrorAction SilentlyContinue}
