param([ValidateSet('system_snapshot','network_snapshot','spooler_status','start_spooler','restore_spooler_stopped')][string]$Operation)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object Text.UTF8Encoding($false)
try {
    $raw=[Console]::In.ReadToEnd()
    $payload=if($raw.Trim()){ $raw | ConvertFrom-Json }else{ [pscustomobject]@{} }
    $result=$null
    switch($Operation) {
        'system_snapshot' {
            $os=Get-CimInstance Win32_OperatingSystem
            $disks=@(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
                @{drive=$_.DeviceID;size_bytes=[long]$_.Size;free_bytes=[long]$_.FreeSpace}
            })
            $result=@{observed_at=[DateTime]::UtcNow.ToString('o');os=$os.Caption;version=$os.Version;
                memory_total_kib=[long]$os.TotalVisibleMemorySize;memory_free_kib=[long]$os.FreePhysicalMemory;disks=$disks}
        }
        'network_snapshot' {
            $adapters=@(Get-NetAdapter | Select-Object -First 16 | ForEach-Object {
                @{interface_index=$_.ifIndex;name=$_.Name;status=[string]$_.Status;link_speed=[string]$_.LinkSpeed}
            })
            $result=@{observed_at=[DateTime]::UtcNow.ToString('o');adapters=$adapters;
                limitations=@('Adapter state is not proof of DNS, internet or target application reachability.')}
        }
        'spooler_status' {
            $service=Get-Service -Name Spooler
            $result=@{name='Spooler';status=[string]$service.Status;observed_at=[DateTime]::UtcNow.ToString('o')}
        }
        default {
            $principal=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
            if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'elevation_required'}
            if($Operation -eq 'start_spooler') {
                if($payload.expected_status -ne 'Stopped' -or (Get-Service Spooler).Status -ne 'Stopped'){throw 'service_state_changed'}
                Start-Service -Name Spooler
            } else {
                if((Get-Service Spooler).Status -ne 'Stopped'){Stop-Service -Name Spooler}
            }
            $result=@{name='Spooler';status=[string](Get-Service Spooler).Status;observed_at=[DateTime]::UtcNow.ToString('o');changed=$true}
        }
    }
    @{ok=$true;evidence=$result}|ConvertTo-Json -Depth 8 -Compress
} catch {
    $code=if($_.Exception.Message -in @('elevation_required','service_state_changed')){$_.Exception.Message}else{'native_failure'}
    @{ok=$false;code=$code}|ConvertTo-Json -Compress
    exit 1
}
