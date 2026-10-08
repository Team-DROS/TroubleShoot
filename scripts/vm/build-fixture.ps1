param([string]$OutputDirectory=(Join-Path $env:TEMP 'TroubleShootFreshFixture'))
$ErrorActionPreference='Stop'
if($PSVersionTable.PSEdition -ne 'Desktop'){throw 'Run with Windows PowerShell 5.1 (powershell.exe), not pwsh.'}
# Fresh synthetic WPF controls expose native UI Automation toggle semantics.
$directory=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $directory -Force | Out-Null
$executable=Join-Path $directory 'TroubleShootFixture.exe'
if(Test-Path -LiteralPath $executable){throw 'Fixture already exists; choose a new output directory.'}
$source=@'
using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Automation;
using System.Windows.Threading;
public static class FreshFixture {
    [STAThread] public static void Main() {
        Application app=new Application();
        Window form=new Window();form.Title="TroubleShoot fresh fixture";
        form.Width=480;form.Height=240;form.WindowStartupLocation=WindowStartupLocation.CenterScreen;
        StackPanel panel=new StackPanel();panel.Margin=new Thickness(20);
        CheckBox feature=new CheckBox();feature.Content="Enable demonstration feature";
        AutomationProperties.SetName(feature,"Enable demonstration feature");
        feature.Margin=new Thickness(0,10,0,20);
        CheckBox save=new CheckBox();save.Content="Require save confirmation";
        AutomationProperties.SetName(save,"Require save confirmation");
        save.IsChecked=true;save.Margin=new Thickness(0,0,0,20);
        TextBlock status=new TextBlock();status.Text="Synthetic controller test only";
        feature.Checked+=(s,e)=>status.Text="Feature state: True";
        feature.Unchecked+=(s,e)=>status.Text="Feature state: False";
        panel.Children.Add(feature);panel.Children.Add(save);panel.Children.Add(status);form.Content=panel;
        Window confirmation=null;
        string cleanup=System.Reflection.Assembly.GetExecutingAssembly().Location+".cleanup";
        DispatcherTimer timer=new DispatcherTimer();timer.Interval=TimeSpan.FromMilliseconds(200);
        timer.Tick+=(s,e)=>{
            if(File.Exists(cleanup)) {
                save.IsChecked=false;
                if(confirmation!=null)confirmation.Close();
                else {timer.Stop();form.Close();}
            }
        };timer.Start();
        form.Closing+=(s,e)=>{
            if(save.IsChecked==true) {
                e.Cancel=true;
                confirmation=new Window();confirmation.Title="Fixture save confirmation";
                confirmation.Width=320;confirmation.Height=140;confirmation.Owner=form;
                Button cancel=new Button();cancel.Content="Cancel";cancel.Width=100;cancel.Height=30;
                cancel.Click+=(sender,args)=>confirmation.Close();confirmation.Content=cancel;
                confirmation.ShowDialog();confirmation=null;
            }
        };
        app.Run(form);
    }
}
'@
$wpf=Join-Path $env:SystemRoot 'Microsoft.NET\Framework64\v4.0.30319\WPF'
$references=@('System.dll','System.Xaml.dll',(Join-Path $wpf 'WindowsBase.dll'),(Join-Path $wpf 'PresentationCore.dll'),(Join-Path $wpf 'PresentationFramework.dll'),(Join-Path $wpf 'UIAutomationTypes.dll'))
Add-Type -TypeDefinition $source -ReferencedAssemblies $references -OutputAssembly $executable -OutputType WindowsApplication
Write-Output $executable
