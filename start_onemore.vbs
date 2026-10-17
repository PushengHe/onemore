Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")

folder = files.GetParentFolderName(WScript.ScriptFullName)
localPython = folder & "\tools\Python310\python.exe"

If Not files.FileExists(localPython) Then
    MsgBox "Python not found at:" & vbCrLf & localPython & vbCrLf & vbCrLf & "Please place Python 3.10+ in the tools\Python310 folder.", vbCritical, "OneMore"
    WScript.Quit 1
End If

ret = shell.Run("""" & localPython & """ -c ""import sys; sys.exit(sys.version_info < (3, 10))"" >nul 2>&1", 0, True)
If ret <> 0 Then
    MsgBox "Python at tools\Python310 must be version 3.10 or newer.", vbCritical, "OneMore"
    WScript.Quit 1
End If

shell.CurrentDirectory = folder
shell.Run """" & folder & "\start_onemore.bat"" """ & localPython & """", 0, False

Set processes = GetObject("winmgmts:root\cimv2")
For attempt = 1 To 100
    For Each process In processes.ExecQuery("SELECT ProcessId FROM Win32_Process WHERE Name = 'python.exe' AND CommandLine LIKE '%main.py%'")
        If shell.AppActivate(CLng(process.ProcessId)) Then WScript.Quit 0
    Next
    WScript.Sleep 200
Next
WScript.Quit 1