param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
if($PSVersionTable.PSEdition -ne 'Desktop'){throw 'Windows PowerShell 5.1 required'}
New-Item -ItemType Directory -Path $OutputDirectory -Force|Out-Null
$exe=Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) 'TroubleShootFixture.exe'
if(Test-Path -LiteralPath $exe){throw 'Use a new fixture directory'}
$source=@'
using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Automation;
using System.Windows.Threading;
public static class FreshMouseFixture {
    [STAThread] public static void Main() {
        Application app=new Application();Window window=new Window();
        window.Title="TroubleShoot mouse fixture";window.Width=620;window.Height=680;
        window.WindowStartupLocation=WindowStartupLocation.CenterScreen;
        Grid grid=new Grid();StackPanel panel=new StackPanel();panel.Margin=new Thickness(20);grid.Children.Add(panel);window.Content=grid;
        int clicks=0,doubles=0;bool cancelOnClick=false;
        string cancelPath=Path.Combine(Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location),"cancel-mid");
        TextBlock clickState=new TextBlock();clickState.Text="Clicks: 0";
        TextBlock doubleState=new TextBlock();doubleState.Text="Double clicks: 0";
        Button button=new Button();button.Content="Count clicks";button.Height=45;
        AutomationProperties.SetName(button,"Count clicks");
        button.Click+=(s,e)=>{clickState.Text="Clicks: "+(++clicks);if(cancelOnClick)File.WriteAllText(cancelPath,"cancel");};
        button.PreviewMouseDown+=(s,e)=>{if(e.ClickCount==2)doubleState.Text="Double clicks: "+(++doubles);};
        panel.Children.Add(button);panel.Children.Add(clickState);panel.Children.Add(doubleState);
        Slider slider=new Slider();slider.Minimum=0;slider.Maximum=100;slider.Value=10;
        slider.Height=35;slider.Margin=new Thickness(0,20,0,5);
        AutomationProperties.SetName(slider,"Test slider");
        TextBlock sliderState=new TextBlock();sliderState.Text="Slider: 10";
        slider.ValueChanged+=(s,e)=>sliderState.Text="Slider: "+slider.Value.ToString("0");
        panel.Children.Add(slider);panel.Children.Add(sliderState);
        TextBlock scrollState=new TextBlock();scrollState.Text="Scroll offset: 0";
        ListBox list=new ListBox();list.Height=200;list.Margin=new Thickness(0,20,0,5);
        AutomationProperties.SetName(list,"Test scroll list");
        for(int n=0;n<30;n++)list.Items.Add("Fixture item "+n);
        list.AddHandler(ScrollViewer.ScrollChangedEvent,new ScrollChangedEventHandler((s,e)=>scrollState.Text="Scroll offset: "+e.VerticalOffset.ToString("0")));
        panel.Children.Add(list);panel.Children.Add(scrollState);
        Button resize=new Button();resize.Content="Resize fixture";resize.Height=30;
        resize.Click+=(s,e)=>window.Width+=40;panel.Children.Add(resize);
        PasswordBox secret=new PasswordBox();secret.Password="dummy";
        secret.HorizontalAlignment=HorizontalAlignment.Stretch;secret.VerticalAlignment=VerticalAlignment.Top;
        secret.Height=45;secret.Margin=new Thickness(20,20,20,0);
        Button overlay=new Button();overlay.Content="Toggle secret overlay";overlay.Height=30;
        overlay.Click+=(s,e)=>{if(grid.Children.Contains(secret))grid.Children.Remove(secret);else grid.Children.Add(secret);};
        panel.Children.Add(overlay);
        Window cover=null;Button coverButton=new Button();coverButton.Content="Toggle cover";coverButton.Height=30;
        coverButton.Click+=(s,e)=>{
            if(cover!=null){cover.Close();cover=null;}
            else {
                var point=button.PointToScreen(new Point(0,0));cover=new Window();cover.Title="Fixture cover";
                cover.Owner=window;cover.Width=button.ActualWidth;cover.Height=button.ActualHeight+60;
                cover.Left=point.X;cover.Top=point.Y;cover.ShowActivated=false;cover.Topmost=true;
                cover.Content=new TextBlock(){Text="Covered fixture button"};cover.Show();
            }
        };panel.Children.Add(coverButton);
        Button arm=new Button();arm.Content="Arm cancellation";arm.Height=25;
        arm.Click+=(s,e)=>cancelOnClick=true;panel.Children.Add(arm);
        DispatcherTimer timer=new DispatcherTimer();timer.Interval=TimeSpan.FromMilliseconds(200);
        string cleanup=System.Reflection.Assembly.GetExecutingAssembly().Location+".cleanup";
        timer.Tick+=(s,e)=>{if(File.Exists(cleanup)){timer.Stop();window.Close();}};timer.Start();
        app.Run(window);
    }
}
'@
$wpf=Join-Path $env:SystemRoot 'Microsoft.NET\Framework64\v4.0.30319\WPF'
$refs=@('System.dll','System.Xaml.dll',(Join-Path $wpf 'WindowsBase.dll'),(Join-Path $wpf 'PresentationCore.dll'),(Join-Path $wpf 'PresentationFramework.dll'),(Join-Path $wpf 'UIAutomationTypes.dll'))
Add-Type -TypeDefinition $source -ReferencedAssemblies $refs -OutputAssembly $exe -OutputType WindowsApplication
$exe
