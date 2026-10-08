$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Security
$form=New-Object Windows.Forms.Form
$form.Text='TroubleShoot: hosted Gemma API setup';$form.Size=New-Object Drawing.Size(480,215)
$form.StartPosition='CenterScreen';$form.TopMost=$true;$form.FormBorderStyle='FixedDialog';$form.MaximizeBox=$false
$label=New-Object Windows.Forms.Label
$label.Text='Enter your Google AI Studio API key locally. It is encrypted for your Windows account and stays in the backend; never paste it into chat.'
$label.SetBounds(15,15,440,55);$form.Controls.Add($label)
$inputKey=New-Object Windows.Forms.TextBox;$inputKey.UseSystemPasswordChar=$true;$inputKey.SetBounds(15,80,440,28);$form.Controls.Add($inputKey)
$save=New-Object Windows.Forms.Button;$save.Text='Save API key';$save.SetBounds(200,125,120,30);$save.DialogResult='OK';$form.Controls.Add($save)
$cancel=New-Object Windows.Forms.Button;$cancel.Text='Cancel';$cancel.SetBounds(330,125,120,30);$cancel.DialogResult='Cancel';$form.Controls.Add($cancel)
$form.AcceptButton=$save;$form.CancelButton=$cancel
try{
    if($form.ShowDialog() -eq 'OK' -and $inputKey.Text.Trim().Length -gt 10){
        $directory=Join-Path $env:LOCALAPPDATA 'TroubleShoot'
        [IO.Directory]::CreateDirectory($directory)|Out-Null
        $bytes=[Text.Encoding]::UTF8.GetBytes($inputKey.Text.Trim())
        $encrypted=[Security.Cryptography.ProtectedData]::Protect($bytes,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser)
        [IO.File]::WriteAllBytes((Join-Path $directory 'api-key.dpapi'),$encrypted)
        [Array]::Clear($bytes,0,$bytes.Length)
    }
}finally{$inputKey.Clear();$form.Dispose()}
