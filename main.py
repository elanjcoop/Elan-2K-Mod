from pymem import *
from pymem.process import *
import time
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal

import time


"""
Rebound home offensive (short) - 19E23B0
Rebound away offensive (short) - 19E2834 / 01DE2834
Shot clock (int, seconds) - 19EE654
Time remaining in quarter (float, seconds) - 19EE638
Period (short) - 19EE5EC
Home team score (short) - 19E2188, 1C18D2C
Away team score (short) - 19E260C
The bug number - 0.3000000119

BUGS:
- If you start a new game with correction in off rebs, you will see 14 secs before tipoff (tipoff immediately fixes tho so no biggie).
- Fewer than 24 seconds left in quarter will not reset shot clock to target_shot_clock even if it's still a valid shot clock time
(if shot clock target is < 24).
- Offensive rebound will auto trigger to target_shot_clock_reset even if the current shot clock > target_shot_clock_reset;
This is a problem that cannot be solved simply due to auto 24 reset prior to logical time evaluation.


TO DO:
Play halves
Disable ELO score system
"""

SHOT_CLOCK_ADDRESS = 0x19EE654
HOME_OFF_REB_ADDRESS = 0x19E23B0
AWAY_OFF_REB_ADDRESS = 0x19E2834
PERIOD_ADDRESS = 0x19EE5EC
PERIOD_TIME_LEFT = 0x19EE638
BACKCOURT_TIME_LEFT_ADDRESS = 0x19EE670
HOME_SCORE_ADDRESS = 0x19E2188
AWAY_SCORE_ADDRESS = 0x19E260C
SHOT_LENGTH_ADDRESS = 0x1A16290
THREE_POINTER_VALUE_ADDRESS = 0x19EE944
INTERNAL_GAME_YEAR_ADDRESS = 0xF32918
HOME_GAME_FOULS_ADDRESS = 0x19E2540
AWAY_GAME_FOULS_ADDRESS = 0x19E29C4
FREE_THROWS_REMAINING_ADDRESS = 0x19EE8DC
FREE_THROWS_VALUE_ADDRESS = 0x19EE94C

OFFICIAL_RULES_SHOT_CLOCK = 24.0000
OFFICIAL_BACKCOURT_TIME = 8

target_shot_clock_full = 24.000001
target_shot_clock_reset = 14.000001
target_target_score = 5
target_overtime_deadline = 3600.0

prev_home_off_reb_count, prev_away_off_reb_count = 0, 0

has_overtime = False

overtime_start_home_score, overtime_start_away_score = 0, 0
home_team_fouls, away_team_fouls = 0,0
time_remaining = 0.0

mem, module = 0, 0

lbl_please_open_game = 0
game_opened = False

target_score_enabled = False
ten_second_violation_enabled = False
halves_enabled = False
g_league_free_throw_rule_enabled = False

def set_shot_clock_full(input_shot_clock_full):
    try:
        input_shot_clock_full = float(input_shot_clock_full)
    except:
        input_shot_clock_full = 24.000001
    if input_shot_clock_full != 0 and input_shot_clock_full != 24 and input_shot_clock_full != None:
        global target_shot_clock_full
        target_shot_clock_full = float(input_shot_clock_full) + 0.000001
    else:
        target_shot_clock_full = 24.000001

def set_shot_clock_reset(input_shot_clock_reset):
    try:
        float(input_shot_clock_reset)
    except:
        input_shot_clock_reset = 14.000001
    if input_shot_clock_reset != "":
        global target_shot_clock_reset
        target_shot_clock_reset = float(input_shot_clock_reset) + 0.000001
    else:
        target_shot_clock_reset = 14.000001

def set_target_score(input_target_score):
    try:
        input_target_score = int(input_target_score)
    except:
        input_target_score = 5
    if input_target_score > 0:
        global target_target_score
        target_target_score = input_target_score
    else:
        target_target_score = 5

def set_overtime_deadline(input_overtime_deadline):
    try:
        input_overtime_deadline = float(input_overtime_deadline)
    except:
        input_overtime_deadline = 60.0
    if input_overtime_deadline > 0.0:
        global target_overtime_deadline
        target_overtime_deadline = input_overtime_deadline * 60.0
    else:
        target_overtime_deadline = 3600.0

def check_overtime_started(mem, module):
    if mem.read_short(module + PERIOD_ADDRESS) == 5:
        global has_overtime, overtime_start_home_score, overtime_start_away_score
        overtime_start_home_score = mem.read_short(module + HOME_SCORE_ADDRESS)
        overtime_start_away_score = mem.read_short(module + AWAY_SCORE_ADDRESS)
        has_overtime = True

def new_game():
    global overtime_start_home_score, overtime_start_away_score, prev_home_off_reb_count, prev_away_off_reb_count, has_overtime
    overtime_start_home_score, overtime_start_away_score, prev_home_off_reb_count, prev_away_off_reb_count = 0, 0, 0, 0
    has_overtime = False
    print("New game!")

def sync_rebounds(mem, module):
    global prev_home_off_reb_count, prev_away_off_reb_count
    prev_home_off_reb_count = mem.read_short(module + HOME_OFF_REB_ADDRESS)
    prev_away_off_reb_count = mem.read_short(module + AWAY_OFF_REB_ADDRESS)

def check_four_pointer(mem, module):
    if mem.read_float(module + SHOT_LENGTH_ADDRESS) > 762.0:
        mem.write_short(module + THREE_POINTER_VALUE_ADDRESS, 4)
    else:
        mem.write_short(module + THREE_POINTER_VALUE_ADDRESS, 3)

def g_league_free_throw_rule(mem, module):
    global away_team_fouls, home_team_fouls, time_remaining
    #print("HI")
    if mem.read_short(module + FREE_THROWS_REMAINING_ADDRESS) > 1:
        time_remaining = mem.read_float(module + PERIOD_TIME_LEFT)
        fts_remaining = mem.read_short(module + FREE_THROWS_REMAINING_ADDRESS)
        print(fts_remaining)
        mem.write_short(module + FREE_THROWS_VALUE_ADDRESS, fts_remaining)
        mem.write_short(module + FREE_THROWS_REMAINING_ADDRESS, 1)
    if time_remaining != mem.read_float(module + PERIOD_TIME_LEFT):
        mem.write_short(module + FREE_THROWS_VALUE_ADDRESS, 1)
        time_remaining = mem.read_float(module + PERIOD_TIME_LEFT)


#If first free throw goes in, there is a bug.
def check_target_score_reached(mem, module):
    global has_overtime, overtime_start_home_score, overtime_start_away_score
    #if mem.read_float(module + PERIOD_TIME_LEFT) == 0.30000001192092896:
        #mem.write_float(module + PERIOD_TIME_LEFT, 0.0)
    if (mem.read_short(module + HOME_SCORE_ADDRESS) - overtime_start_home_score >= target_target_score or
        mem.read_short(module + AWAY_SCORE_ADDRESS) - overtime_start_away_score >= target_target_score):  
        mem.write_float(module + PERIOD_TIME_LEFT, 0.00000000000000000)
        print("Current home score: ", mem.read_short(module + HOME_SCORE_ADDRESS), " vs start of OT: ", overtime_start_home_score, sep = '')
        print("Current away score: ", mem.read_short(module + AWAY_SCORE_ADDRESS), " vs start of OT: ", overtime_start_away_score, sep = '')
        print("Game over!")
    if mem.read_short(module + PERIOD_ADDRESS) != 5:
        has_overtime = False
        print("New game!")

class QThread1(QtCore.QThread):
    sig = pyqtSignal(str)
    def run(self, *args, **kwargs):
        while True:
            start_mod()

def start_mod():
    global game_opened
    try:
        mem = Pymem("nba2k14.exe")
        module = module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
        prev_home_off_reb_count = mem.read_short(module + HOME_OFF_REB_ADDRESS)
        prev_away_off_reb_count = mem.read_short(module + AWAY_OFF_REB_ADDRESS)
    except:
        pass
    while game_opened == False:
        try:
            mem = Pymem("nba2k14.exe")
            module = module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
            game_opened = True
        except pymem.exception.ProcessNotFound:
                print("Please open NBA 2K14.")
                time.sleep(5)
        except:
            pass

    while True:
        try:
            global has_overtime
            if mem.read_short(module + HOME_OFF_REB_ADDRESS) != prev_home_off_reb_count:
                mem.write_float(module + SHOT_CLOCK_ADDRESS, target_shot_clock_reset)
                prev_home_off_reb_count = mem.read_short(module + HOME_OFF_REB_ADDRESS)
                prev_away_off_reb_count = mem.read_short(module + AWAY_OFF_REB_ADDRESS)
                print("Home team offensive rebound! Soft reset shot clock with ", round(mem.read_float(module + PERIOD_TIME_LEFT), 2), " remaining in Q", mem.read_short(module + PERIOD_ADDRESS), sep = '')
            elif mem.read_short(module + AWAY_OFF_REB_ADDRESS) != prev_away_off_reb_count:
                mem.write_float(module + SHOT_CLOCK_ADDRESS, target_shot_clock_reset)
                prev_home_off_reb_count = mem.read_short(module + HOME_OFF_REB_ADDRESS)
                prev_away_off_reb_count = mem.read_short(module + AWAY_OFF_REB_ADDRESS)
                print("Away team offensive rebound! Soft reset shot clock with ", round(mem.read_float(module + PERIOD_TIME_LEFT), 2), " remaining in Q", mem.read_short(module + PERIOD_ADDRESS), sep = '')
            elif mem.read_float(module + SHOT_CLOCK_ADDRESS) == OFFICIAL_RULES_SHOT_CLOCK:
                mem.write_float(module + SHOT_CLOCK_ADDRESS, target_shot_clock_full)
                #print("Shot clock reset with ", round(mem.read_float(module + PERIOD_TIME_LEFT), 2), " remaining in Q", mem.read_short(module + PERIOD_ADDRESS), sep = '')
            if ten_second_violation_enabled:
                if mem.read_float(module + BACKCOURT_TIME_LEFT_ADDRESS) == OFFICIAL_BACKCOURT_TIME:
                    mem.write_float(module + BACKCOURT_TIME_LEFT_ADDRESS, 10.0)
            if halves_enabled:
                if mem.read_short(module + PERIOD_ADDRESS) == 2:
                    mem.write_short(module + PERIOD_ADDRESS, 4)
            if target_score_enabled:
                if not has_overtime:
                    check_overtime_started(mem, module)
                else:
                    if mem.read_float(module + PERIOD_TIME_LEFT) % 60 == 0.0000 and mem.read_float(module + PERIOD_TIME_LEFT) > 0.4:
                        mem.write_float(module + PERIOD_TIME_LEFT, target_overtime_deadline)
                    check_target_score_reached(mem, module)
            else:
                has_overtime = False
            #check_four_pointer()
            if g_league_free_throw_rule_enabled:
                g_league_free_throw_rule(mem, module)
        except:
            exit

def window():
    app = QApplication(sys.argv)
    win = QMainWindow()

    win.setGeometry(1200, 300, 350, 500)
    win.setWindowTitle("Elan's Mod")
    win.setWindowIcon(QIcon("ja.jpg"))
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    win.setWindowIcon(QIcon(resource_path('resources/images/ja.jpg')))
    win.setToolTip("Ja")

    lbl_please_open_game = QtWidgets.QLabel(win)
    lbl_please_open_game.setText("")
    lbl_please_open_game.move(50, 25)
    lbl_please_open_game.setLineWidth(100)

    lbl_shot_clock = QtWidgets.QLabel(win)
    lbl_shot_clock.setText("Shot Clock: ")
    lbl_shot_clock.move(50, 50)

    lbl_reset_shot_clock = QtWidgets.QLabel(win)
    lbl_reset_shot_clock.setText("Reset Shot Clock:")
    lbl_reset_shot_clock.move(50, 90)

    lbl_ten_second_violation = QtWidgets.QLabel(win)
    lbl_ten_second_violation.setText("10 Second Backcourt Violation")
    lbl_ten_second_violation.move(50,130)
    
    lbl_enable_target_score = QtWidgets.QLabel(win)
    lbl_enable_target_score.setText("Target Score")
    lbl_enable_target_score.move(50,170)

    lbl_target_score = QtWidgets.QLabel(win)
    lbl_target_score.setText("OT Target Score:")
    lbl_target_score.move(50, 210)

    lbl_overtime_deadline = QtWidgets.QLabel(win)
    lbl_overtime_deadline.setText("OT Deadline (minutes):")
    lbl_overtime_deadline.adjustSize()
    lbl_overtime_deadline.move(50, 250)
    
    lbl_enable_halves = QtWidgets.QLabel(win)
    lbl_enable_halves.setText("Two Halves")
    lbl_enable_halves.move(50, 290)

    lbl_gleague_ft_rule = QtWidgets.QLabel(win)
    lbl_gleague_ft_rule.setText("G-League FT Rule")
    lbl_gleague_ft_rule.move(50, 330)

    lbl_internal_game_year = QtWidgets.QLabel(win)
    lbl_internal_game_year.setText("Internal Game Year")
    lbl_internal_game_year.move(50, 370)

    txt_shot_clock = QtWidgets.QLineEdit(win)
    txt_shot_clock.move(200, 50)
    txt_shot_clock.setPlaceholderText("24")
    txt_shot_clock.setText("24")

    txt_reset_shot_clock = QtWidgets.QLineEdit(win)
    txt_reset_shot_clock.move(200, 90)
    txt_reset_shot_clock.setPlaceholderText("14")
    txt_reset_shot_clock.setText("14")

    checkbox_enable_ten_second = QtWidgets.QCheckBox(win)
    checkbox_enable_ten_second.setChecked(False)
    checkbox_enable_ten_second.move(200, 130)

    def enable_target_score_clicked(self):
        global target_score_enabled
        if checkbox_enable_target_score.isChecked():
            print("Target score on.")
            txt_target_score.setDisabled(False)
            txt_overtime_deadline.setDisabled(False)
            target_score_enabled = True
        else:
            print("Target score off.")
            txt_target_score.setDisabled(True)
            txt_overtime_deadline.setDisabled(True)
            target_score_enabled = False

    checkbox_enable_target_score = QtWidgets.QCheckBox(win)
    checkbox_enable_target_score.setChecked(False)
    checkbox_enable_target_score.move(200, 170)
    checkbox_enable_target_score.clicked.connect(enable_target_score_clicked)

    txt_target_score = QtWidgets.QLineEdit(win)
    txt_target_score.move(200, 210)
    txt_target_score.setDisabled(True)
    txt_target_score.setText("5")
    
    txt_overtime_deadline = QtWidgets.QLineEdit(win)
    txt_overtime_deadline.move(200, 250)
    txt_overtime_deadline.setDisabled(True)
    txt_overtime_deadline.setText("10")

    checkbox_enable_halves = QtWidgets.QCheckBox(win)
    checkbox_enable_halves.setChecked(False)
    checkbox_enable_halves.move(200, 290)

    checkbox_gleague_ft_rule = QtWidgets.QCheckBox(win)
    checkbox_gleague_ft_rule.setChecked(False)
    checkbox_gleague_ft_rule.move(200, 330)

    txt_internal_game_date_year = QtWidgets.QLineEdit(win)
    txt_internal_game_date_year.move(200, 370)
    txt_internal_game_date_year.setPlaceholderText("2013")
    txt_internal_game_date_year.setText("2013")

    def apply_clicked(self):
        print("New values applied.")
        set_shot_clock_full(txt_shot_clock.text())
        set_shot_clock_reset(txt_reset_shot_clock.text())
        set_target_score(txt_target_score.text())
        set_overtime_deadline(txt_overtime_deadline.text())
        global ten_second_violation_enabled, halves_enabled, g_league_free_throw_rule_enabled
        if checkbox_enable_ten_second.isChecked():
            print("Ten second backcourt enabled.")
            ten_second_violation_enabled = True
        else:
            print("Ten second backcourt disabled.")
            ten_second_violation_enabled = False
        if checkbox_enable_halves.isChecked():
            print("Halves enabled.")
            halves_enabled = True
            pass
        else:
            print("Halves disabled.")
            halves_enabled = False
            pass
        if checkbox_gleague_ft_rule.isChecked():
            print("G-League FTs: Enabled")
            g_league_free_throw_rule_enabled = True
        else:
            print("G-League FTs: Disabled")
            g_league_free_throw_rule_enabled = False
        try:
            mem = Pymem("nba2k14.exe")
            module = module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
            lbl_please_open_game.setText("")
            if int(txt_internal_game_date_year.text()) >= 0:
                mem.write_short(module + INTERNAL_GAME_YEAR_ADDRESS, int(txt_internal_game_date_year.text()))
        except:
            lbl_please_open_game.setText("Please open NBA 2K14 / illegal game year.")
            lbl_please_open_game.setStyleSheet('QLabel{color: red}')
            lbl_please_open_game.adjustSize()

    btn_apply = QtWidgets.QPushButton(win)
    btn_apply.setText("Apply")
    btn_apply.clicked.connect(apply_clicked)
    btn_apply.move(200, 410)
    thread1 = QThread1()
    thread1.start()

    win.show()
    sys.exit(app.exec_())

window()