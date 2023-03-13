# Elan-2K-Mod
Read more about the mod here:
https://forums.nba-live.com/viewtopic.php?f=153&t=114893

How to start:
Simply open dist/Elan's Mod.exe

How to build for yourself:
Pre-1. Delete build/ and dist/ folders (recursively) and main.spec
1. Go to directory containing main.py
2. Run "pyinstaller --onefile main.py"
3. In main.spec, set datas=[('resources', 'resources')]
4. Set "Console" to "False"
4. Set "Name" to whatever you please
5. Add "icon='ja.ico'" as your final line in the exe group of arguments, or whatever icon you please
6. Run "pyinstaller main.spec"