param([ValidateSet('list_targets','observe','capture','toggle_checkbox','graceful_close','mouse_move','mouse_click','mouse_double_click','mouse_scroll','mouse_drag')][string]$Operation)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object Text.UTF8Encoding($false)
try {
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    Add-Type -AssemblyName System.Drawing
    if(-not ('TSWindow' -as [type])) { Add-Type @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class TSWindow {
    [StructLayout(LayoutKind.Sequential)] public struct Rect { public int Left,Top,Right,Bottom; }
    public delegate bool EnumProc(IntPtr h, IntPtr p);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc callback,IntPtr param);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out Rect r);
    [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr c);
    [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
    [DllImport("user32.dll",SetLastError=true)] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags);
    [DllImport("user32.dll",SetLastError=true)] public static extern bool PostMessage(IntPtr h,uint m,UIntPtr w,IntPtr l);
    public static long[] Visible() {
        var list=new List<long>();
        EnumWindows((h,p)=>{if(IsWindowVisible(h))list.Add(h.ToInt64());return true;},IntPtr.Zero);
        return list.ToArray();
    }
    public static uint Pid(IntPtr h){uint p;GetWindowThreadProcessId(h,out p);return p;}
    public static Rect Bounds(IntPtr h){Rect r;if(!GetWindowRect(h,out r))throw new Exception("target_changed");return r;}
    public static string Title(IntPtr h){var b=new StringBuilder(256);GetWindowText(h,b,256);return b.ToString();}
}
'@
    }
    . (Join-Path $PSScriptRoot 'mouse-native.ps1')
    [TSWindow]::SetThreadDpiAwarenessContext([IntPtr](-4)) | Out-Null
    $raw=[Console]::In.ReadToEnd()
    $payload=if($raw.Trim()){$raw|ConvertFrom-Json}else{[pscustomobject]@{}}
    $denied=@('powershell','pwsh','cmd','WindowsTerminal','wt','conhost','consent','CredentialUIBroker','LogonUI','winlogon','regedit','mmc','Taskmgr','explorer','msedge','chrome','firefox','SystemSettings')
    function Identity([long]$handle) {
        $h=[IntPtr]$handle
        if(-not [TSWindow]::IsWindow($h) -or -not [TSWindow]::IsWindowVisible($h) -or [TSWindow]::IsIconic($h)){throw 'hidden_target'}
        $windowPid=[TSWindow]::Pid($h)
        $process=Get-Process -Id $windowPid
        if($process.ProcessName -in $denied){throw 'protected_target'}
        return @{handle=$handle;pid=[int]$windowPid;started=$process.StartTime.ToUniversalTime().ToString('o')}
    }
    function SameTarget($expected,$current) {
        return ($expected.handle -eq $current.handle -and $expected.pid -eq $current.pid -and $expected.started -eq $current.started)
    }
    function Bounding($r) {
        return @{left=[int]$r.Left;top=[int]$r.Top;width=[int]($r.Right-$r.Left);height=[int]($r.Bottom-$r.Top)}
    }
    function ControlRows($root) {
        $walker=[Windows.Automation.TreeWalker]::ControlViewWalker
        $queue=New-Object Collections.Queue
        $queue.Enqueue(@($root,0))
        $rows=New-Object Collections.Generic.List[object]
        $visited=0
        while($queue.Count -and $visited -lt 80) {
            $entry=$queue.Dequeue();$element=$entry[0];$depth=[int]$entry[1];$visited++
            $c=$element.Current
            $type=$c.ControlType.ProgrammaticName.Replace('ControlType.','')
            if($c.IsPassword -or $type -in @('Edit','Document')){$script:captureSafe=$false;continue}
            $toggle=$null
            if($type -eq 'CheckBox') {
                try {$toggle=[string]([Windows.Automation.TogglePattern]$element.GetCurrentPattern([Windows.Automation.TogglePattern]::Pattern)).Current.ToggleState}catch{}
            }
            $id=($element.GetRuntimeId() -join '.')
            $name=[string]$c.Name
            if($name.Length -gt 120){$name=$name.Substring(0,120)}
            $rows.Add(@{control_id=$id;type=$type;name=$name;enabled=$c.IsEnabled;offscreen=$c.IsOffscreen;
                toggle_state=$toggle;bounds=@{left=$c.BoundingRectangle.Left;top=$c.BoundingRectangle.Top;width=$c.BoundingRectangle.Width;height=$c.BoundingRectangle.Height}})
            if($depth -lt 4) {
                $child=$walker.GetFirstChild($element);$siblings=0
                while($null -ne $child -and $siblings -lt 24 -and $queue.Count -lt 80) {
                    $queue.Enqueue(@($child,($depth+1)));$child=$walker.GetNextSibling($child);$siblings++
                }
                if($null -ne $child){$script:captureSafe=$false}
            } elseif($null -ne $walker.GetFirstChild($element)) {
                $script:captureSafe=$false
            }
        }
        if($queue.Count){$script:captureSafe=$false}
        return $rows.ToArray()
    }
    function Snapshot([long]$handle) {
        $target=Identity $handle
        $h=[IntPtr]$handle
        $root=[Windows.Automation.AutomationElement]::FromHandle($h)
        $script:captureSafe=$true
        $controls=@(ControlRows $root)
        if(-not (SameTarget $target (Identity $handle))){throw 'target_changed'}
        return @{target=$target;observed_at=[DateTime]::UtcNow.ToString('o');bounds=(Bounding ([TSWindow]::Bounds($h)));
            dpi=[int][TSWindow]::GetDpiForWindow($h);foreground=([TSWindow]::GetForegroundWindow() -eq $h);controls=$controls;capture_allowed=$script:captureSafe;
            cursor=@([TSMouse]::Cursor());virtual_screen=@([TSMouse]::Virtual());client_bounds=(BoundingClient ([TSMouse]::Client($handle)))}
    }
    function BoundingClient($r){return @{left=$r[0];top=$r[1];width=$r[2];height=$r[3]}}
    function CheckSnapshot($expected) {
        $age=([DateTimeOffset]::UtcNow-[DateTimeOffset]::Parse($expected.observed_at)).TotalSeconds
        if($age -lt 0 -or $age -gt 5){throw 'stale_observation'}
        $fresh=Snapshot $expected.target.handle
        if(-not (SameTarget $expected.target $fresh.target)){throw 'target_changed'}
        foreach($key in @('left','top','width','height')){if($expected.bounds.$key -ne $fresh.bounds.$key){throw 'geometry_changed'}}
        if($expected.dpi -ne $fresh.dpi){throw 'geometry_changed'}
        if(-not $fresh.foreground){throw 'foreground_changed'}
        return $fresh
    }
    function FinalCheck($expected) {
        $age=([DateTimeOffset]::UtcNow-[DateTimeOffset]::Parse($expected.observed_at)).TotalSeconds
        if($age -lt 0 -or $age -gt 5){throw 'stale_observation'}
        if(-not (SameTarget $expected.target (Identity $expected.target.handle))){throw 'target_changed'}
        $h=[IntPtr]$expected.target.handle
        $rect=Bounding ([TSWindow]::Bounds($h))
        foreach($key in @('left','top','width','height')){if($expected.bounds.$key -ne $rect.$key){throw 'geometry_changed'}}
        if($expected.dpi -ne [int][TSWindow]::GetDpiForWindow($h)){throw 'geometry_changed'}
        if([TSWindow]::GetForegroundWindow() -ne $h){throw 'foreground_changed'}
    }
    if($Operation -like 'mouse_*') {
        $mutex=New-Object Threading.Mutex($false,'Local\TroubleShoot.DesktopMouse')
        $acquired=$false
        try {
            try {$acquired=$mutex.WaitOne(0)}catch [Threading.AbandonedMutexException] {$acquired=$true;throw 'mouse_previous_crash'}
            if(-not $acquired){throw 'mouse_busy'}
            $result=Invoke-MouseOperation $Operation $payload
        }finally{if($acquired){$mutex.ReleaseMutex()};$mutex.Dispose()}
    } elseif($Operation -eq 'list_targets') {
        $targets=@()
        foreach($handle in [TSWindow]::Visible()) {
            if($targets.Count -ge 32){break}
            try {
                $target=Identity $handle
                $title=[TSWindow]::Title([IntPtr]$handle)
                if($title){$targets+=@{target=$target;title=$title}}
            }catch{}
        }
        $result=@{targets=$targets}
    } elseif($Operation -eq 'observe') {
        $result=Snapshot $payload.target.handle
        if(-not (SameTarget $payload.target $result.target)){throw 'target_changed'}
    } elseif($Operation -eq 'capture') {
        if($payload.capture_consent -isnot [bool] -or -not $payload.capture_consent){throw 'capture_consent_required'}
        $before=CheckSnapshot $payload.snapshot
        if(-not $before.capture_allowed){throw 'protected_content'}
        $width=$before.bounds.width;$height=$before.bounds.height
        if($width -le 0 -or $height -le 0 -or $width*$height -gt 4000000){throw 'capture_size_limit'}
        $bitmap=New-Object Drawing.Bitmap($width,$height)
        $graphics=[Drawing.Graphics]::FromImage($bitmap)
        $dc=$graphics.GetHdc()
        try {if(-not [TSWindow]::PrintWindow([IntPtr]$before.target.handle,$dc,2)){throw 'capture_failed'}}finally{$graphics.ReleaseHdc($dc)}
        try {
            $after=CheckSnapshot $payload.snapshot
            if(-not $after.capture_allowed){throw 'protected_content'}
            $stream=New-Object IO.MemoryStream
            try {$bitmap.Save($stream,[Drawing.Imaging.ImageFormat]::Png);$result=@{png_base64=[Convert]::ToBase64String($stream.ToArray());target=$after.target}}
            finally{$stream.Dispose()}
        }finally{$graphics.Dispose();$bitmap.Dispose()}
    } elseif($Operation -eq 'toggle_checkbox') {
        $before=CheckSnapshot $payload.snapshot
        if($payload.desired_state -notin @('On','Off')){throw 'control_changed'}
        $expected=$payload.control
        $match=@($before.controls|Where-Object {$_.control_id -eq $expected.control_id})
        if($match.Count -ne 1 -or $match[0].type -ne 'CheckBox' -or -not $match[0].enabled -or $match[0].offscreen -or $match[0].name -ne $expected.name -or $match[0].toggle_state -ne $expected.toggle_state){throw 'control_changed'}
        foreach($key in @('left','top','width','height')){if($match[0].bounds.$key -ne $expected.bounds.$key){throw 'control_changed'}}
        $box=$match[0].bounds;$window=$before.bounds
        if($box.width -le 0 -or $box.height -le 0 -or $box.left -lt $window.left -or $box.top -lt $window.top -or ($box.left+$box.width) -gt ($window.left+$window.width) -or ($box.top+$box.height) -gt ($window.top+$window.height)){throw 'control_changed'}
        $root=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]$before.target.handle)
        $walker=[Windows.Automation.TreeWalker]::ControlViewWalker
        $queue=New-Object Collections.Queue;$queue.Enqueue($root);$selected=$null;$visited=0
        while($queue.Count -and $visited -lt 100) {
            $element=$queue.Dequeue();$visited++
            if(($element.GetRuntimeId() -join '.') -eq $expected.control_id){$selected=$element;break}
            $child=$walker.GetFirstChild($element);$siblings=0
            while($null -ne $child -and $siblings -lt 24 -and $queue.Count -lt 100){$queue.Enqueue($child);$child=$walker.GetNextSibling($child);$siblings++}
        }
        if($null -eq $selected -or $selected.Current.IsPassword -or $selected.Current.ControlType -ne [Windows.Automation.ControlType]::CheckBox){throw 'control_changed'}
        $pattern=[Windows.Automation.TogglePattern]$selected.GetCurrentPattern([Windows.Automation.TogglePattern]::Pattern)
        FinalCheck $payload.snapshot
        if([string]$pattern.Current.ToggleState -ne $expected.toggle_state){throw 'control_changed'}
        if([string]$pattern.Current.ToggleState -ne $payload.desired_state){$pattern.Toggle()}
        $after=Snapshot $before.target.handle
        $current=@($after.controls|Where-Object {$_.control_id -eq $expected.control_id})
        $result=@{postcondition_met=($current.Count -eq 1 -and $current[0].toggle_state -eq $payload.desired_state);after=$after}
    } else {
        $before=CheckSnapshot $payload.snapshot
        FinalCheck $payload.snapshot
        if(-not [TSWindow]::PostMessage([IntPtr]$before.target.handle,16,[UIntPtr]::Zero,[IntPtr]::Zero)){throw 'native_failure'}
        $end=[DateTime]::UtcNow.AddSeconds(2)
        while([TSWindow]::IsWindow([IntPtr]$before.target.handle) -and [DateTime]::UtcNow -lt $end){Start-Sleep -Milliseconds 100}
        $remaining=0
        foreach($handle in [TSWindow]::Visible()) {
            try{if([TSWindow]::Pid([IntPtr]$handle) -eq $before.target.pid){$remaining++}}catch{}
        }
        $result=@{postcondition_met=(-not [TSWindow]::IsWindow([IntPtr]$before.target.handle) -and $remaining -eq 0);
            target_still_exists=[TSWindow]::IsWindow([IntPtr]$before.target.handle);remaining_process_windows=$remaining}
    }
    @{ok=$true;evidence=$result}|ConvertTo-Json -Depth 16 -Compress
}catch {
    $known=@('hidden_target','protected_target','protected_content','target_changed','stale_observation','geometry_changed','foreground_changed','capture_consent_required','capture_size_limit','capture_failed','control_changed',
        'mouse_input_cancelled','emergency_stop','user_input_active','user_cursor_moved','point_outside','point_occluded','invalid_mouse_arguments','input_delivery_failed','cursor_position_failed','cursor_unavailable','mouse_busy','mouse_previous_crash','double_click_expired')
    $code=if($_.Exception.Message -in $known){$_.Exception.Message}else{'native_failure'}
    @{ok=$false;code=$code}|ConvertTo-Json -Compress
    exit 1
}
