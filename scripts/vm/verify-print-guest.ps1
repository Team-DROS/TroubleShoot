# Developer symptom probe: an installed Microsoft PDF printer is required.
# Does not install drivers, change services or print to an external device.
$ErrorActionPreference='Stop'
if($env:TROUBLESHOOT_VM_TEST -ne '1'){throw 'Disposable guest marker required'}
$report=@{observed_at=[DateTime]::UtcNow.ToString('o');physical_print_verified=$false;pdf_print_verified=$false;spooler=[string](Get-Service Spooler).Status}
$printer=Get-CimInstance Win32_Printer|Where-Object {$_.Name -eq 'Microsoft Print to PDF' -and $_.DriverName -eq 'Microsoft Print To PDF'}
if(@($printer).Count -ne 1){
    $report.status='blocked';$report.reason='Microsoft Print to PDF is not installed; service state is not print verification'
}else{
    Add-Type -AssemblyName System.Drawing
    $output=Join-Path $PSScriptRoot ('PrintProbe-'+[guid]::NewGuid().ToString('N')+'.pdf')
    $document=New-Object Drawing.Printing.PrintDocument
    $document.PrinterSettings.PrinterName='Microsoft Print to PDF'
    $document.PrinterSettings.PrintToFile=$true;$document.PrinterSettings.PrintFileName=$output
    $document.PrintController=New-Object Drawing.Printing.StandardPrintController
    $document.add_PrintPage({param($sender,$event)
        $font=New-Object Drawing.Font('Arial',18)
        try{$event.Graphics.DrawString('TroubleShoot fresh print verification',$font,[Drawing.Brushes]::Black,40,40);$event.HasMorePages=$false}
        finally{$font.Dispose()}
    })
    try{
        $document.Print()
        $deadline=[DateTime]::UtcNow.AddSeconds(15)
        while(-not (Test-Path $output) -and [DateTime]::UtcNow -lt $deadline){Start-Sleep -Milliseconds 200}
        if(Test-Path $output){
            $bytes=[IO.File]::ReadAllBytes($output)
            $report.pdf_print_verified=($bytes.Length -gt 100 -and [Text.Encoding]::ASCII.GetString($bytes,0,5) -eq '%PDF-')
            $report.output_bytes=$bytes.Length
        }
        $report.status=if($report.pdf_print_verified){'partial'}else{'failed'}
        $report.limitations='PDF output signature only; rendered page contents and physical printing are not verified.'
    }catch{$report.status='failed';$report.reason='Print probe failed; no success claim'}
    finally{$document.Dispose()}
}
$report|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'print-probe-result.json') -Encoding UTF8
$report|ConvertTo-Json -Depth 5 -Compress
