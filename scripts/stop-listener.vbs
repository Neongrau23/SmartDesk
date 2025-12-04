Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Aktuelles Verzeichnis des VBS-Skripts
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Pfade relativ zum Script-Verzeichnis
pythonExe = objFSO.BuildPath(scriptDir, "..\src\smartdesk\.venv\Scripts\python.exe")
mainPy = objFSO.BuildPath(scriptDir, "..\src\smartdesk\main.py")

' Befehl ausführen (versteckt, ohne Fenster)
objShell.Run """" & pythonExe & """ """ & mainPy & """ stop-listener", 0, False