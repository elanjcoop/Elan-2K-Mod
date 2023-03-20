# ELAN'S GAME-CHANGING 2K MOD

## FEATURES
* Customize the Shot Clock
* Reset the Shot Clock on Offensive Boards (post-2018 NBA Update)
* No 3-Pointers Mode
* 10-Second Backcourt Violation (College, High School)
* Target Score (Default: G-League)
* Two Halves (College)
* G-League FT Rule
* Change the Internal Game Year


## START IT UP
Simply open dist/Elan's Mod.exe

## MAKE IT YOUR OWN
How to build for yourself:
1. Delete build/ and dist/ folders (recursively) and main.spec
2. Go to directory containing main.py
3. Run "pyinstaller --onefile main.py"
4. Wait for that command to finish running, then in main.spec, set datas=[('resources', 'resources')]
5. Under the EXE grouping, Set "Console" to "False"
6. Set "Name" to whatever you please
7. Add "icon='ja.ico'" as your final line in the exe group of arguments, or whatever icon you please
8. Run "pyinstaller main.spec"
9. If you renamed in Step 6, delete "main.exe" and run RENAMED_FILE.exe

## MORE
Read more about the mod here:
https://forums.nba-live.com/viewtopic.php?f=153&t=114893

## SIDE EFFECTS
1. Winning on first free throw with target score on will have players walk around for a while.
2. Shooting foul on shortened threes will onl;y lead to two shots, not three.

## AGENDA
1. Add settings.ini for value saving.
2. Add ability to override quarter length.
3. Create tutorial for tool.
4. Create consistency with Apply button.
5. Add four-pointers.