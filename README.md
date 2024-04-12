# ELAN'S GAME-CHANGING 2K MOD

## FEATURES
* Customize the Shot Clock
* Reset the Shot Clock on Offensive Boards (post-2018 NBA Update)
* No 3-Pointers Mode
* 3-Point Line Shortened (High School, College, '94-'96 NBA)
* 10-Second Backcourt Violation (College, High School)
* Target Score (Default: G-League)
* Two Halves (College)
* G-League FT Rule
* Change the Internal Game Year
* Override Period Length

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

## SIDE EFFECTS
1. Winning on first free throw with target score on will have players walk around for a while.
2. Shooting foul on shortened threes will only lead to two shots, not three.

## KNOWN BUGS
1. Offensive rebounds triggering shot clock resets are detected too often.
2. Running the mod before the game loads will likely lead to "override period length" not working.
3. Automake shots selectively works

## AGENDA
1. Create tutorial for tool.
2. Create consistency with Apply button.
3. Make qualifying shortened threes receive a 3-Pt foul shot.

## MORE
Read more about the mod here:
https://forums.nba-live.com/viewtopic.php?f=153&t=114893