# VM harness only. Fixed Escape/Control presses, never exposed as agent tools.
if($env:TROUBLESHOOT_VM_TEST -ne '1'){throw 'Only run in the explicitly marked guest test session'}
if(-not ('TSMouseTestKeys' -as [type])) { Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Threading;
public static class TSMouseTestKeys {
    [StructLayout(LayoutKind.Sequential)] public struct Mouse {public int X,Y;public uint Data,Flags,Time;public UIntPtr Extra;}
    [StructLayout(LayoutKind.Sequential)] public struct Key {public ushort Vk,Scan;public uint Flags,Time;public UIntPtr Extra;}
    [StructLayout(LayoutKind.Explicit)] public struct Union {[FieldOffset(0)]public Mouse Mouse;[FieldOffset(0)]public Key Key;}
    [StructLayout(LayoutKind.Sequential)] public struct Input {public uint Type;public Union Union;}
    [DllImport("user32.dll",SetLastError=true)] static extern uint SendInput(uint count,Input[] input,int size);
    static void Send(ushort key,bool up){Input i=new Input();i.Type=1;i.Union.Key.Vk=key;i.Union.Key.Flags=up?2u:0u;if(SendInput(1,new Input[]{i},Marshal.SizeOf(typeof(Input)))!=1)throw new Exception("Test key input refused");}
    public static void HoldEscape(){Send(27,false);}
    public static void ReleaseEscape(){Send(27,true);}
    public static void HoldControl(){Send(17,false);}
    public static void ReleaseControl(){Send(17,true);}
    static Thread lockThread;static ManualResetEvent ready,release;
    public static void StartLock(){
        ready=new ManualResetEvent(false);release=new ManualResetEvent(false);
        lockThread=new Thread(()=>{using(var m=new Mutex(false,"Local\\TroubleShoot.DesktopMouse")){m.WaitOne();ready.Set();try{release.WaitOne();}finally{m.ReleaseMutex();}}});
        lockThread.IsBackground=true;lockThread.Start();if(!ready.WaitOne(2000))throw new Exception("Test mutex was not acquired");
    }
    public static void StopLock(){if(lockThread!=null){release.Set();lockThread.Join(2000);lockThread=null;ready.Dispose();release.Dispose();}}
}
'@ }
