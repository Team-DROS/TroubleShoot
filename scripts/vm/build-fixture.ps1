param([string]$OutputDirectory=(Join-Path $env:TEMP 'TroubleShootFreshFixture'))
$ErrorActionPreference='Stop'
if($PSVersionTable.PSEdition -ne 'Desktop'){throw 'Run this build with Windows PowerShell 5.1 (powershell.exe), not pwsh.'}
# Newly authored synthetic UI; no real repair is claimed by this fixture.
$directory=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $directory -Force | Out-Null
$executable=Join-Path $directory 'TroubleShootFixture.exe'
if(Test-Path -LiteralPath $executable){throw 'Fixture already exists; choose a new output directory.'}
$source=@'
using System;
using System.Drawing;
using System.Windows.Forms;
public static class FreshFixture {
    [STAThread] public static void Main() {
        Application.EnableVisualStyles();
        Form form=new Form();
        form.Text="TroubleShoot fresh fixture";
        form.ClientSize=new Size(480,220);
        form.StartPosition=FormStartPosition.CenterScreen;
        CheckBox feature=new CheckBox();
        feature.Text="Enable demonstration feature";
        feature.SetBounds(20,30,350,30);
        CheckBox save=new CheckBox();
        save.Text="Require save confirmation";
        save.Checked=true;
        save.SetBounds(20,80,350,30);
        Label status=new Label();
        status.Text="Synthetic controller test only";
        status.SetBounds(20,140,420,40);
        feature.CheckedChanged+=(s,e)=>status.Text="Feature state: "+feature.Checked;
        form.Controls.Add(feature);form.Controls.Add(save);form.Controls.Add(status);
        form.FormClosing+=(s,e)=>{
            if(save.Checked) {
                var answer=MessageBox.Show(form,"Unsaved fixture state. Close?","Fixture save confirmation",MessageBoxButtons.OKCancel);
                if(answer!=DialogResult.OK)e.Cancel=true;
            }
        };
        Application.Run(form);
    }
}
'@
Add-Type -TypeDefinition $source -ReferencedAssemblies System.Windows.Forms,System.Drawing -OutputAssembly $executable -OutputType WindowsApplication
Write-Output $executable
