# Native input has no shell/keyboard API. Private fixed worker helper, not a model action.
if(-not ('TSMouse' -as [type])) { Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class TSMouse {
    [StructLayout(LayoutKind.Sequential)] public struct Point {public int X,Y;public Point(int x,int y){X=x;Y=y;}}
    [StructLayout(LayoutKind.Sequential)] public struct Rect {public int L,T,R,B;}
    [StructLayout(LayoutKind.Sequential)] public struct Mouse {public int X,Y;public uint Data,Flags,Time;public UIntPtr Extra;}
    [StructLayout(LayoutKind.Explicit)] public struct Union {[FieldOffset(0)] public Mouse Mouse;}
    [StructLayout(LayoutKind.Sequential)] public struct Input {public uint Type;public Union Union;}
    [DllImport("user32.dll",SetLastError=true)] static extern uint SendInput(uint count,Input[] input,int size);
    [DllImport("user32.dll")] static extern bool GetCursorPos(out Point point);
    [DllImport("user32.dll")] static extern int GetSystemMetrics(int index);
    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int key);
    [DllImport("user32.dll")] static extern uint GetDoubleClickTime();
    [DllImport("user32.dll")] static extern IntPtr WindowFromPoint(Point point);
    [DllImport("user32.dll")] static extern IntPtr GetAncestor(IntPtr window,uint flags);
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr window,out Rect rect);
    [DllImport("user32.dll")] static extern bool ClientToScreen(IntPtr window,ref Point point);
    public static int[] Cursor(){Point p;if(!GetCursorPos(out p))throw new Exception("cursor_unavailable");return new int[]{p.X,p.Y};}
    public static int[] Virtual(){return new int[]{GetSystemMetrics(76),GetSystemMetrics(77),GetSystemMetrics(78),GetSystemMetrics(79)};}
    public static int[] Client(long window){Rect r;if(!GetClientRect(new IntPtr(window),out r))throw new Exception("target_changed");Point p=new Point(r.L,r.T);if(!ClientToScreen(new IntPtr(window),ref p))throw new Exception("target_changed");return new int[]{p.X,p.Y,r.R-r.L,r.B-r.T};}
    public static long RootAt(int x,int y){return GetAncestor(WindowFromPoint(new Point(x,y)),2).ToInt64();}
    public static bool Escape(){return (GetAsyncKeyState(27)&0x8000)!=0;}
    public static uint DoubleClickTime(){return GetDoubleClickTime();}
    public static bool Busy(){foreach(int key in new int[]{1,2,4,5,6,16,17,18,91,92})if((GetAsyncKeyState(key)&0x8000)!=0)return true;return false;}
    static Input Event(uint flags,int x,int y,uint data){Input i=new Input();i.Type=0;i.Union.Mouse.Flags=flags;i.Union.Mouse.X=x;i.Union.Mouse.Y=y;i.Union.Mouse.Data=data;return i;}
    static Input Absolute(int x,int y){var v=Virtual();if(v[2]<=0||v[3]<=0||x<v[0]||y<v[1]||x>=v[0]+v[2]||y>=v[1]+v[3])throw new Exception("point_outside");int nx=(int)Math.Floor(((double)x-v[0]+0.5)*65536/v[2]);int ny=(int)Math.Floor(((double)y-v[1]+0.5)*65536/v[3]);return Event(0xC001,Math.Min(65535,nx),Math.Min(65535,ny),0);}
    static void Send(Input[] events){uint sent=SendInput((uint)events.Length,events,Marshal.SizeOf(typeof(Input)));if(sent!=(uint)events.Length){SendInput(1,new Input[]{Event(4,0,0,0)},Marshal.SizeOf(typeof(Input)));throw new Exception("input_delivery_failed");}}
    public static void Move(int x,int y){Send(new Input[]{Absolute(x,y)});}
    public static void Click(){Send(new Input[]{Event(2,0,0,0),Event(4,0,0,0)});}
    public static void Scroll(int ticks){Send(new Input[]{Event(0x800,0,0,unchecked((uint)(ticks*120)))});}
    public static void Drag(int x,int y,int tx,int ty){
        // One short atomic input batch; never sleep while holding a button.
        Input[] events=new Input[10];events[0]=Event(2,0,0,0);
        for(int n=1;n<=8;n++)events[n]=Absolute((int)Math.Round(x+(tx-x)*n/8.0),(int)Math.Round(y+(ty-y)*n/8.0));
        events[9]=Event(4,0,0,0);Send(events);
    }
}
'@ }

function Mouse-StateCheck($snapshot,$expectedCursor,$cancelFile) {
    if($cancelFile -and [IO.File]::Exists($cancelFile)){throw 'mouse_input_cancelled'}
    if([TSMouse]::Escape()){throw 'emergency_stop'}
    if([TSMouse]::Busy()){throw 'user_input_active'}
    FinalCheck $snapshot
    $virtual=[TSMouse]::Virtual()
    for($n=0;$n -lt 4;$n++){if($virtual[$n] -ne $snapshot.virtual_screen[$n]){throw 'geometry_changed'}}
    $client=[TSMouse]::Client($snapshot.target.handle)
    for($n=0;$n -lt 4;$n++){if($client[$n] -ne @($snapshot.client_bounds.left,$snapshot.client_bounds.top,$snapshot.client_bounds.width,$snapshot.client_bounds.height)[$n]){throw 'geometry_changed'}}
    $cursor=[TSMouse]::Cursor()
    if([Math]::Abs($cursor[0]-$expectedCursor[0]) -gt 1 -or [Math]::Abs($cursor[1]-$expectedCursor[1]) -gt 1){throw 'user_cursor_moved'}
}

function Mouse-PointCheck($snapshot,$control,[int]$x,[int]$y) {
    $window=$snapshot.bounds;$client=$snapshot.client_bounds;$box=$control.bounds
    if($x -lt 0 -or $y -lt 0 -or $x -ge $window.width -or $y -ge $window.height){throw 'point_outside'}
    $sx=[int]($window.left+$x);$sy=[int]($window.top+$y)
    foreach($r in @($client,$box)) {if($sx -lt $r.left -or $sy -lt $r.top -or $sx -ge ($r.left+$r.width) -or $sy -ge ($r.top+$r.height)){throw 'point_outside'}}
    if([TSMouse]::RootAt($sx,$sy) -ne $snapshot.target.handle){throw 'point_occluded'}
    $hit=[Windows.Automation.AutomationElement]::FromPoint((New-Object Windows.Point($sx,$sy)))
    $walker=[Windows.Automation.TreeWalker]::ControlViewWalker;$matched=$false
    for($n=0;$null -ne $hit -and $n -lt 16;$n++) {
        $c=$hit.Current;$type=$c.ControlType.ProgrammaticName.Replace('ControlType.','')
        if($c.IsPassword -or $type -in @('Edit','Document') -or -not $c.IsEnabled){throw 'protected_content'}
        if(($hit.GetRuntimeId() -join '.') -eq $control.control_id){
            $name=[string]$c.Name;if($name.Length -gt 120){$name=$name.Substring(0,120)}
            if($name -ne $control.name -or $type -ne $control.type -or $c.IsOffscreen){throw 'control_changed'}
            $rect=$c.BoundingRectangle
            if($rect.Left -ne $control.bounds.left -or $rect.Top -ne $control.bounds.top -or $rect.Width -ne $control.bounds.width -or $rect.Height -ne $control.bounds.height){throw 'control_changed'}
            $matched=$true;break
        }
        $hit=$walker.GetParent($hit)
    }
    if(-not $matched){throw 'control_changed'}
    return @($sx,$sy)
}

function Invoke-MouseOperation($operation,$payload) {
    $before=CheckSnapshot $payload.snapshot
    $args=$payload.arguments;$expected=$payload.control
    $fields=@('control_id','x','y');if($operation -eq 'mouse_scroll'){$fields+='ticks'};if($operation -eq 'mouse_drag'){$fields+=@('to_x','to_y')}
    if(@($args.PSObject.Properties.Name).Count -ne $fields.Count){throw 'invalid_mouse_arguments'}
    foreach($field in $fields){if($field -notin $args.PSObject.Properties.Name){throw 'invalid_mouse_arguments'}}
    foreach($field in @('x','y','to_x','to_y','ticks')){
        if($field -in $fields -and ($args.$field -isnot [int] -and $args.$field -isnot [long])){throw 'invalid_mouse_arguments'}
        if($field -in $fields -and $field -ne 'ticks' -and ($args.$field -lt 0 -or $args.$field -gt 32767)){throw 'invalid_mouse_arguments'}
    }
    if($operation -eq 'mouse_scroll' -and ($args.ticks -eq 0 -or [Math]::Abs($args.ticks) -gt 5)){throw 'invalid_mouse_arguments'}
    if($args.control_id -ne $expected.control_id){throw 'control_changed'}
    $controls=@($before.controls|Where-Object {$_.control_id -eq $expected.control_id})
    if($controls.Count -ne 1){throw 'control_changed'}
    $control=$controls[0]
    foreach($key in @('name','type','toggle_state','enabled','offscreen')){if($control.$key -ne $expected.$key){throw 'control_changed'}}
    foreach($key in @('left','top','width','height')){if($control.bounds.$key -ne $expected.bounds.$key){throw 'control_changed'}}
    $types=switch($operation){
        'mouse_move' {@('Button','CheckBox','RadioButton','ListItem','TabItem','Slider','List')}
        'mouse_click' {@('Button','CheckBox','RadioButton','ListItem','TabItem')}
        'mouse_double_click' {@('Button','ListItem')}
        'mouse_scroll' {@('List')}
        'mouse_drag' {@('Slider')}
    }
    if(-not $control.enabled -or $control.offscreen -or $control.type -notin $types){throw 'control_changed'}
    $point=Mouse-PointCheck $before $control $args.x $args.y
    $destination=$null
    if($operation -eq 'mouse_drag'){
        if($args.x -eq $args.to_x -and $args.y -eq $args.to_y){throw 'invalid_mouse_arguments'}
        $destination=Mouse-PointCheck $before $control $args.to_x $args.to_y
        for($n=1;$n -lt 8;$n++){
            Mouse-PointCheck $before $control ([int][Math]::Round($args.x+($args.to_x-$args.x)*$n/8.0)) ([int][Math]::Round($args.y+($args.to_y-$args.y)*$n/8.0))|Out-Null
        }
    }
    Mouse-StateCheck $payload.snapshot $payload.snapshot.cursor $payload.cancel_file
    [TSMouse]::Move($point[0],$point[1])
    $moved=[TSMouse]::Cursor()
    if([Math]::Abs($moved[0]-$point[0]) -gt 1 -or [Math]::Abs($moved[1]-$point[1]) -gt 1){throw 'cursor_position_failed'}
    Mouse-StateCheck $payload.snapshot $point $payload.cancel_file
    Mouse-PointCheck $before $control $args.x $args.y|Out-Null
    Mouse-StateCheck $payload.snapshot $point $payload.cancel_file
    switch($operation) {
        'mouse_click' {[TSMouse]::Click()}
        'mouse_double_click' {
            $timer=[Diagnostics.Stopwatch]::StartNew()
            [TSMouse]::Click();Start-Sleep -Milliseconds 30
            Mouse-StateCheck $payload.snapshot $point $payload.cancel_file
            Mouse-PointCheck $before $control $args.x $args.y|Out-Null
            Mouse-StateCheck $payload.snapshot $point $payload.cancel_file
            if($timer.ElapsedMilliseconds -ge ([TSMouse]::DoubleClickTime()-10)){throw 'double_click_expired'}
            [TSMouse]::Click()
        }
        'mouse_scroll' {[TSMouse]::Scroll($args.ticks)}
        'mouse_drag' {[TSMouse]::Drag($point[0],$point[1],$destination[0],$destination[1])}
    }
    return @{input_delivered=$true;symptom_verified=$false;cursor=@([TSMouse]::Cursor());after=(Snapshot $before.target.handle);
        cancelled=([TSMouse]::Escape() -or ($payload.cancel_file -and [IO.File]::Exists($payload.cancel_file)))}
}
