param([string]$UserName='TROUBLESHOOT')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$authRoot=Join-Path $env:LOCALAPPDATA 'TroubleShootEvent\vm-auth'
New-Item -ItemType Directory -Force -Path $authRoot | Out-Null
$acl=Get-Acl -LiteralPath $authRoot
$acl.SetAccessRuleProtection($true,$false)
$identity=[Security.Principal.WindowsIdentity]::GetCurrent().User
$rule=New-Object Security.AccessControl.FileSystemAccessRule($identity,'FullControl','ContainerInherit,ObjectInherit','None','Allow')
$acl.AddAccessRule($rule)
Set-Acl -LiteralPath $authRoot -AclObject $acl
$form=New-Object Windows.Forms.Form
$form.Text='TroubleShoot: Windows test VM login'
$form.Size=New-Object Drawing.Size(440,245)
$form.StartPosition='CenterScreen'
$form.TopMost=$true
$form.FormBorderStyle='FixedDialog'
$form.MaximizeBox=$false
$message=New-Object Windows.Forms.Label
$message.Text='Guest credentials for TROUBLESHOOT-Test only. Password is masked and stored temporarily for VBoxManage; never sent to chat.'
$message.SetBounds(15,10,400,45)
$form.Controls.Add($message)
$label=New-Object Windows.Forms.Label
$label.Text='Guest user name';$label.SetBounds(15,65,130,22);$form.Controls.Add($label)
$user=New-Object Windows.Forms.TextBox
$user.Text=$UserName;$user.SetBounds(155,62,250,25);$form.Controls.Add($user)
$label2=New-Object Windows.Forms.Label
$label2.Text='Guest password';$label2.SetBounds(15,103,130,22);$form.Controls.Add($label2)
$password=New-Object Windows.Forms.TextBox
$password.UseSystemPasswordChar=$true;$password.SetBounds(155,100,250,25);$form.Controls.Add($password)
$ok=New-Object Windows.Forms.Button
$ok.Text='Use for VM tests';$ok.SetBounds(145,150,140,30);$ok.DialogResult='OK';$form.Controls.Add($ok)
$cancel=New-Object Windows.Forms.Button
$cancel.Text='Cancel';$cancel.SetBounds(295,150,100,30);$cancel.DialogResult='Cancel';$form.Controls.Add($cancel)
$form.AcceptButton=$ok;$form.CancelButton=$cancel
$result=$form.ShowDialog()
$record=Join-Path $authRoot 'login.json'
if($result -ne 'OK') {
    @{status='cancelled'} | ConvertTo-Json | Set-Content -LiteralPath $record -Encoding UTF8
} else {
    $secretFile=Join-Path $authRoot 'password.txt'
    [IO.File]::WriteAllText($secretFile,$password.Text,(New-Object Text.UTF8Encoding($false)))
    @{status='ready';username=$user.Text.Trim();password_file=$secretFile;created_at=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $record -Encoding UTF8
}
$password.Clear();$form.Dispose()
