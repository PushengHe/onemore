Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")

If shell.Run("cmd /d /c where python >nul 2>&1", 0, True) <> 0 Then
    MsgBox "Python was not found. Please install Python 3.10 or newer and add it to PATH." & vbCrLf & "https://www.python.org/downloads/", vbCritical, "OneMore"
    WScript.Quit 1
End If

If shell.Run("cmd /d /c python -c ""import sys; sys.exit(sys.version_info < (3, 10))"" >nul 2>&1", 0, True) <> 0 Then
    MsgBox "A working Python 3.10 or newer installation is required." & vbCrLf & "https://www.python.org/downloads/", vbCritical, "OneMore"
    WScript.Quit 1
End If

folder = files.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = folder
shell.Run "cmd /d /c " & Chr(34) & Chr(34) & folder & "\start_onemore.bat" & Chr(34) & Chr(34), 0, False

Set processes = GetObject("winmgmts:root\cimv2")
For attempt = 1 To 100
    For Each process In processes.ExecQuery("SELECT ProcessId FROM Win32_Process WHERE Name = 'python.exe' AND CommandLine LIKE '%main.py%'")
        If shell.AppActivate(CLng(process.ProcessId)) Then WScript.Quit 0
    Next
    WScript.Sleep 200
Next
WScript.Quit 1