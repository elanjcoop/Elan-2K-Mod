from pymem import *
import pymem.process as process
import time
import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from configparser import ConfigParser


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
"""
### STACK ADDRESSES ###
SHOT_CLOCK_ADDRESS = 0x19EE654
HOME_OFF_REB_ADDRESS = 0x19E23B0
AWAY_OFF_REB_ADDRESS = 0x19E2834
PERIOD_ADDRESS = 0x19EE5EC
PERIOD_TIME_LEFT_ADDRESS = 0x19EE638
BACKCOURT_TIME_LEFT_ADDRESS = 0x19EE670
HOME_SCORE_ADDRESS = 0x19E2188
AWAY_SCORE_ADDRESS = 0x19E260C
SHOT_LENGTH_ADDRESS = 0x1A16290
THREE_POINTER_VALUE_ADDRESS = 0x19EE944
TWO_POINTER_VALUE_ADDRESS = 0x19EE948
INTERNAL_GAME_YEAR_ADDRESS = 0xF32918
HOME_GAME_FOULS_ADDRESS = 0x19E2540
AWAY_GAME_FOULS_ADDRESS = 0x19E29C4
FREE_THROWS_REMAINING_ADDRESS = 0x19EE8DC
FREE_THROWS_VALUE_ADDRESS = 0x19EE94C
ACTIVE_SHOT_ADDRESS = 0x19EE8F8
### HEAP LOCATIONS ###
PERIOD_LENGTH_PN_LOCATION = 0x011472E4
### HEAP OFFSETS ###
PERIOD_LENGTH_PN_OFFSETS = [0x50]

OFFICIAL_RULES_SHOT_CLOCK = 24.0000
OFFICIAL_BACKCOURT_TIME = 8

target_shot_clock_full = 23.999999
target_shot_clock_reset = 13.999999
target_target_score = 5
target_overtime_deadline = 3600.0
shortened_three_point_length = 601.98
override_period_length_value = 20

prev_home_off_reb_count, prev_away_off_reb_count = 0, 0

has_overtime = False

overtime_start_home_score, overtime_start_away_score = 0, 0
home_team_fouls, away_team_fouls = 0,0
time_remaining = 0.0
shot_length = 0
previous_shot_length = 0
start_time = 0

mem, module = 0, 0

lbl_please_open_game = 0
game_opened = False

target_score_enabled = False
ten_second_violation_enabled = False
halves_enabled = False
g_league_free_throw_rule_enabled = False
threes_disabled = False
shorten_threes_enabled = False
override_period_length_enabled = False


def get_pointer_address(mem, module, location, offsets):
    address = mem.read_int(module + location)
    for offset in offsets:
        if offset != offsets[-1]:
            address = mem.read_int(address + offset)
    address = address + offsets[-1]
    return address

def set_shot_clock_full(input_shot_clock_full):
    try:
        input_shot_clock_full = float(input_shot_clock_full)
    except:
        input_shot_clock_full = 23.999999
    if input_shot_clock_full != 0 and input_shot_clock_full != 24 and input_shot_clock_full != None:
        global target_shot_clock_full
        target_shot_clock_full = float(input_shot_clock_full) - 0.000001
    else:
        target_shot_clock_full = 23.999999

def set_shot_clock_reset(input_shot_clock_reset):
    try:
        float(input_shot_clock_reset)
    except:
        input_shot_clock_reset = 13.999999
    if input_shot_clock_reset != "":
        global target_shot_clock_reset
        target_shot_clock_reset = float(input_shot_clock_reset) - 0.000001
    else:
        target_shot_clock_reset = 13.999999

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

def set_shortened_three_length(input_shortened_three_length):
    try:
        input_shortened_three_length = float(input_shortened_three_length)
    except:
        input_shortened_three_length = 23.75
    global shortened_three_point_length
    if input_shortened_three_length > 0.0 and input_shortened_three_length < 99.0:
        shortened_three_point_length = input_shortened_three_length * 30.48
    else:
        shortened_three_point_length = 723.9
    print("Shortened three length: ", shortened_three_point_length, sep = '')

def set_override_period_length(input_period_length):
    try:
        input_period_length = int(input_period_length)
    except:
        input_period_length = 20
    global override_period_length_value
    if input_period_length > 0 and input_period_length < 100:
        override_period_length_value = input_period_length
    else:
        override_period_length_value = 20
    print("Override period length: ", override_period_length_value, sep = '')

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
    if (mem.read_short(module + PERIOD_ADDRESS) <= 3 or
    (mem.read_short(module + PERIOD_ADDRESS) == 4 and mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS) > 120.0)):
        if mem.read_short(module + FREE_THROWS_REMAINING_ADDRESS) > 1:
            time.sleep(2)
            time_remaining = mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS)
            fts_remaining = mem.read_short(module + FREE_THROWS_REMAINING_ADDRESS)
            print("FTs remaining: ", fts_remaining, sep = '')
            mem.write_short(module + FREE_THROWS_VALUE_ADDRESS, fts_remaining)
            mem.write_short(module + FREE_THROWS_REMAINING_ADDRESS, 1)
        if time_remaining != mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS):
            mem.write_short(module + FREE_THROWS_VALUE_ADDRESS, 1)
            time_remaining = mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS)

def threes_off(mem, module):
    if mem.read_short(module + THREE_POINTER_VALUE_ADDRESS) == 3:
        mem.write_short(module + THREE_POINTER_VALUE_ADDRESS, 2)

def shorten_threes(mem, module):
    global shot_length, previous_shot_length, start_time
    shot_length = mem.read_float(module + SHOT_LENGTH_ADDRESS)
    active_shot = (mem.read_short(module + ACTIVE_SHOT_ADDRESS) == 1)
    if shot_length > shortened_three_point_length and shot_length != previous_shot_length:
        mem.write_short(module + TWO_POINTER_VALUE_ADDRESS, 3)
    if not active_shot and time.time() - start_time > 1:
        mem.write_short(module + TWO_POINTER_VALUE_ADDRESS, 2)
        previous_shot_length = shot_length
        start_time = time.time()


#If first free throw goes in, there is a bug.
def check_target_score_reached(mem, module):
    global has_overtime, overtime_start_home_score, overtime_start_away_score
    #if mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS) == 0.30000001192092896:
        #mem.write_float(module + PERIOD_TIME_LEFT_ADDRESS, 0.0)
    if (mem.read_short(module + HOME_SCORE_ADDRESS) - overtime_start_home_score >= target_target_score or
        mem.read_short(module + AWAY_SCORE_ADDRESS) - overtime_start_away_score >= target_target_score):  
        mem.write_float(module + PERIOD_TIME_LEFT_ADDRESS, 0.00000000000000000)
        print("Current home score: ", mem.read_short(module + HOME_SCORE_ADDRESS), " vs start of OT: ", overtime_start_home_score, sep = '')
        print("Current away score: ", mem.read_short(module + AWAY_SCORE_ADDRESS), " vs start of OT: ", overtime_start_away_score, sep = '')
        print("Game over!")
    if mem.read_short(module + PERIOD_ADDRESS) != 5:
        has_overtime = False
        print("New game!")

def override_period_length(mem, module):
    global override_period_length_enabled
    PERIOD_LENGTH_PN_ADDRESS = get_pointer_address(mem, module, PERIOD_LENGTH_PN_LOCATION, PERIOD_LENGTH_PN_OFFSETS)
    mem.write_int(PERIOD_LENGTH_PN_ADDRESS, override_period_length_value)
    override_period_length_enabled = False

class QThread1(QtCore.QThread):
    sig = pyqtSignal(str)
    def run(self, *args, **kwargs):
        while True:
            start_mod()

def start_mod():
    global game_opened
    try:
        mem = Pymem("nba2k14.exe")
        module = process.module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
        prev_home_off_reb_count = mem.read_short(module + HOME_OFF_REB_ADDRESS)
        prev_away_off_reb_count = mem.read_short(module + AWAY_OFF_REB_ADDRESS)
    except:
        pass
    while game_opened == False:
        try:
            mem = Pymem("nba2k14.exe")
            module = process.module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
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
                print("Home team offensive rebound! Soft reset shot clock with ", round(mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS), 2), " remaining in Q", mem.read_short(module + PERIOD_ADDRESS), sep = '')
            elif mem.read_short(module + AWAY_OFF_REB_ADDRESS) != prev_away_off_reb_count:
                mem.write_float(module + SHOT_CLOCK_ADDRESS, target_shot_clock_reset)
                prev_home_off_reb_count = mem.read_short(module + HOME_OFF_REB_ADDRESS)
                prev_away_off_reb_count = mem.read_short(module + AWAY_OFF_REB_ADDRESS)
                print("Away team offensive rebound! Soft reset shot clock with ", round(mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS), 2), " remaining in Q", mem.read_short(module + PERIOD_ADDRESS), sep = '')
            elif mem.read_float(module + SHOT_CLOCK_ADDRESS) == OFFICIAL_RULES_SHOT_CLOCK:
                mem.write_float(module + SHOT_CLOCK_ADDRESS, target_shot_clock_full)
                #print("Shot clock reset with ", round(mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS), 2), " remaining in Q", mem.read_short(module + PERIOD_ADDRESS), sep = '')
            if shorten_threes_enabled:
                shorten_threes(mem, module)
            else:
                if mem.read_short(module + TWO_POINTER_VALUE_ADDRESS) != 2:
                    mem.write_short(module + TWO_POINTER_VALUE_ADDRESS, 2)
                    print("Reverted 3-Pt Shortening.")
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
                    if mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS) % 60 == 0.0000 and mem.read_float(module + PERIOD_TIME_LEFT_ADDRESS) > 0.4:
                        mem.write_float(module + PERIOD_TIME_LEFT_ADDRESS, target_overtime_deadline)
                    check_target_score_reached(mem, module)
            else:
                has_overtime = False
            #check_four_pointer()
            if g_league_free_throw_rule_enabled:
                g_league_free_throw_rule(mem, module)
            if threes_disabled:
                threes_off(mem, module)
            else:
                if mem.read_short(module + THREE_POINTER_VALUE_ADDRESS) == 2:
                    mem.write_short(module + THREE_POINTER_VALUE_ADDRESS, 3)
            if override_period_length_enabled:
                override_period_length(mem, module)
        except:
            exit

def window():
    app = QApplication(sys.argv)
    win = QMainWindow()

    win.setGeometry(1200, 300, 400, 700)
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

    parser = ConfigParser()
    parser.read(resource_path('dev.cfg'))

    lbl_please_open_game = QtWidgets.QLabel(win)
    lbl_please_open_game.setText("")
    lbl_please_open_game.move(40, 25)
    lbl_please_open_game.setLineWidth(100)

    lbl_shot_clock = QtWidgets.QLabel(win)
    lbl_shot_clock.setText("Shot Clock: ")
    lbl_shot_clock.move(40, 50)
    #lbl_shot_clock.setToolTip("Bonjour")

    lbl_reset_shot_clock = QtWidgets.QLabel(win)
    lbl_reset_shot_clock.setText("Reset Shot Clock:")
    lbl_reset_shot_clock.move(40, 90)

    lbl_ten_second_violation = QtWidgets.QLabel(win)
    lbl_ten_second_violation.setText("10 Second Backcourt Violation")
    lbl_ten_second_violation.move(40,130)
    
    lbl_enable_target_score = QtWidgets.QLabel(win)
    lbl_enable_target_score.setText("Target Score")
    lbl_enable_target_score.move(40,170)

    lbl_target_score = QtWidgets.QLabel(win)
    lbl_target_score.setText("OT Target Score:")
    lbl_target_score.move(40, 210)

    lbl_overtime_deadline = QtWidgets.QLabel(win)
    lbl_overtime_deadline.setText("OT Deadline (minutes):")
    lbl_overtime_deadline.adjustSize()
    lbl_overtime_deadline.move(40, 250)
    
    lbl_enable_halves = QtWidgets.QLabel(win)
    lbl_enable_halves.setText("Two Halves")
    lbl_enable_halves.move(40, 290)

    lbl_gleague_ft_rule = QtWidgets.QLabel(win)
    lbl_gleague_ft_rule.setText("G-League FT Rule")
    lbl_gleague_ft_rule.move(40, 330)

    lbl_internal_game_year = QtWidgets.QLabel(win)
    lbl_internal_game_year.setText("Internal Game Year")
    lbl_internal_game_year.move(40, 370)

    lbl_disable_threes = QtWidgets.QLabel(win)
    lbl_disable_threes.setText("Disable 3-Pointers?")
    lbl_disable_threes.move(40, 410)

    lbl_enable_shortened_threes = QtWidgets.QLabel(win)
    lbl_enable_shortened_threes.setText("Shorten 3-Pointers?")
    lbl_enable_shortened_threes.move(40, 450)

    lbl_shortened_threes = QtWidgets.QLabel(win)
    lbl_shortened_threes.setText("3-Point length (ft):")
    lbl_shortened_threes.move(40, 490)

    lbl_override_period_length = QtWidgets.QLabel(win)
    lbl_override_period_length.setText("Override period length?")
    lbl_override_period_length.move(40, 530)
    lbl_override_period_length.setFixedWidth(140)

    lbl_period_length = QtWidgets.QLabel(win)
    lbl_period_length.setText("Period length (minutes):")
    lbl_period_length.move(40, 570)
    lbl_period_length.setFixedWidth(140)

    txt_shot_clock = QtWidgets.QLineEdit(win)
    txt_shot_clock.move(230, 50)
    txt_shot_clock.setPlaceholderText("24")

    txt_reset_shot_clock = QtWidgets.QLineEdit(win)
    txt_reset_shot_clock.move(230, 90)
    txt_reset_shot_clock.setPlaceholderText("14")

    checkbox_enable_ten_second = QtWidgets.QCheckBox(win)
    checkbox_enable_ten_second.move(230, 130)

    def enable_target_score_clicked(self):
        global target_score_enabled
        if checkbox_enable_target_score.isChecked():
            print("Target score on.")
            txt_target_score.setDisabled(False)
            txt_overtime_deadline.setDisabled(False)
            target_score_enabled = True
            parser.set('settings', 'target_score_enabled', 'True')
        else:
            print("Target score off.")
            txt_target_score.setDisabled(True)
            txt_overtime_deadline.setDisabled(True)
            target_score_enabled = False
            parser.set('settings', 'target_score_enabled', 'False')
        with open(resource_path("dev.cfg"), "w") as f:
            parser.write(f)

    checkbox_enable_target_score = QtWidgets.QCheckBox(win)
    checkbox_enable_target_score.move(230, 170)
    checkbox_enable_target_score.clicked.connect(enable_target_score_clicked)

    txt_target_score = QtWidgets.QLineEdit(win)
    txt_target_score.move(230, 210)
    
    txt_overtime_deadline = QtWidgets.QLineEdit(win)
    txt_overtime_deadline.move(230, 250)

    checkbox_enable_halves = QtWidgets.QCheckBox(win)
    checkbox_enable_halves.move(230, 290)

    checkbox_gleague_ft_rule = QtWidgets.QCheckBox(win)
    checkbox_gleague_ft_rule.move(230, 330)

    txt_internal_game_date_year = QtWidgets.QLineEdit(win)
    txt_internal_game_date_year.move(230, 370)
    txt_internal_game_date_year.setPlaceholderText("2013")

    def disable_threes(self):
        global shorten_threes_enabled, threes_disabled
        if checkbox_disable_threes.isChecked():
            print("3s: Disabled")
            threes_disabled = True
            checkbox_shorten_threes.setChecked(False)
            enable_shortened_threes(checkbox_shorten_threes)
            checkbox_shorten_threes.setDisabled(True)
            parser.set('settings', 'disable_three_pointers_enabled', 'True')
        else:
            print("3s: Enabled")
            threes_disabled = False
            checkbox_shorten_threes.setDisabled(False)
            parser.set('settings', 'disable_three_pointers_enabled', 'False')
        with open(resource_path("dev.cfg"), "w") as f:
            parser.write(f)

    checkbox_disable_threes = QtWidgets.QCheckBox(win)
    checkbox_disable_threes.move(230, 410)
    checkbox_disable_threes.clicked.connect(disable_threes)

    def enable_shortened_threes(self):
        global shorten_threes_enabled
        if checkbox_shorten_threes.isChecked():
            print("Shortened threes on.")
            txt_shortened_threes_length.setDisabled(False)
            shorten_threes_enabled = True
            parser.set('settings', 'shorten_three_pointers_enabled', 'True')
        else:
            print("Shortened threes off.")
            txt_shortened_threes_length.setDisabled(True)
            shorten_threes_enabled = False
            parser.set('settings', 'shorten_three_pointers_enabled', 'False')
        with open(resource_path("dev.cfg"), "w") as f:
            parser.write(f)
    
    checkbox_shorten_threes = QtWidgets.QCheckBox(win)
    checkbox_shorten_threes.move(230, 450)
    checkbox_shorten_threes.clicked.connect(enable_shortened_threes)

    txt_shortened_threes_length = QtWidgets.QLineEdit(win)
    txt_shortened_threes_length.move(230, 490)

    def override_period_length(self):
        global override_period_length_enabled
        if checkbox_override_period_length.isChecked():
            print("Override game length enabled.")
            txt_override_period_length.setDisabled(False)
            override_period_length_enabled = True
            parser.set('settings', 'override_period_length_enabled', 'True')
        else:
            print("Override game length disabled.")
            txt_override_period_length.setDisabled(True)
            override_period_length_enabled = False
            parser.set('settings', 'override_period_length_enabled', 'False')
        with open(resource_path("dev.cfg"), "w") as f:
            parser.write(f)

    checkbox_override_period_length = QtWidgets.QCheckBox(win)
    checkbox_override_period_length.move(230, 530)
    checkbox_override_period_length.clicked.connect(override_period_length)

    txt_override_period_length = QtWidgets.QLineEdit(win)
    txt_override_period_length.move(230, 570)


    def apply_clicked(self = None):
        print("New values applied.")
        set_shot_clock_full(txt_shot_clock.text())
        set_shot_clock_reset(txt_reset_shot_clock.text())
        set_target_score(txt_target_score.text())
        set_overtime_deadline(txt_overtime_deadline.text())
        set_shortened_three_length(txt_shortened_threes_length.text())
        set_override_period_length(txt_override_period_length.text())
        global ten_second_violation_enabled, halves_enabled, g_league_free_throw_rule_enabled, threes_disabled, override_period_length_enabled
        if checkbox_enable_ten_second.isChecked():
            print("Ten second backcourt enabled.")
            ten_second_violation_enabled = True
            parser.set('settings', 'ten_second_backcourt_enabled', 'True')
        else:
            print("Ten second backcourt disabled.")
            ten_second_violation_enabled = False
            parser.set('settings', 'ten_second_backcourt_enabled', 'False')
        if checkbox_enable_halves.isChecked():
            print("Halves enabled.")
            halves_enabled = True
            parser.set('settings', 'two_halves_enabled', 'True')
        else:
            print("Halves disabled.")
            halves_enabled = False
            parser.set('settings', 'two_halves_enabled', 'False')
        if checkbox_gleague_ft_rule.isChecked():
            print("G-League FTs: Enabled")
            g_league_free_throw_rule_enabled = True
            parser.set('settings', 'g_league_ft_rule_enabled', 'True')
        else:
            print("G-League FTs: Disabled")
            g_league_free_throw_rule_enabled = False
            parser.set('settings', 'g_league_ft_rule_enabled', 'False')
        try:
            mem = Pymem("nba2k14.exe")
            module = process.module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
            lbl_please_open_game.setText("")
            if int(txt_internal_game_date_year.text()) >= 0:
                mem.write_short(module + INTERNAL_GAME_YEAR_ADDRESS, int(txt_internal_game_date_year.text()))
                parser.set('settings', 'internal_game_year', txt_internal_game_date_year.text())
        except:
            lbl_please_open_game.setText("Please open NBA 2K14 / illegal game year.")
            lbl_please_open_game.setStyleSheet('QLabel{color: red}')
            lbl_please_open_game.adjustSize()
        parser.set('settings', 'shot_clock', txt_shot_clock.text())
        parser.set('settings', 'reset_shot_clock', txt_reset_shot_clock.text())
        parser.set('settings', 'ot_target_score', txt_target_score.text())
        parser.set('settings', 'ot_deadline', txt_overtime_deadline.text())
        parser.set('settings', 'shortened_three_pointer_length', txt_shortened_threes_length.text())
        parser.set('settings', 'period_length', txt_override_period_length.text())
        with open(resource_path("dev.cfg"), "w") as f:
            parser.write(f)
        
    txt_shot_clock.setText(parser.get('settings', 'shot_clock'))
    txt_reset_shot_clock.setText(parser.get('settings', 'reset_shot_clock'))
    checkbox_enable_ten_second.setChecked(parser.get('settings', 'ten_second_backcourt_enabled') == 'True')
    checkbox_enable_target_score.setChecked(parser.get('settings', 'target_score_enabled') == 'True')
    txt_target_score.setDisabled(parser.get('settings', 'target_score_enabled') == 'False')
    txt_target_score.setText(parser.get('settings', 'ot_target_score'))
    txt_overtime_deadline.setDisabled(parser.get('settings', 'target_score_enabled') == 'False')
    txt_overtime_deadline.setText(parser.get('settings', 'ot_deadline'))
    checkbox_enable_halves.setChecked(parser.get('settings', 'two_halves_enabled') == 'True')
    checkbox_gleague_ft_rule.setChecked(parser.get('settings', 'g_league_ft_rule_enabled') == 'True')
    txt_internal_game_date_year.setText(parser.get('settings', 'internal_game_year'))
    checkbox_disable_threes.setChecked(parser.get('settings', 'disable_three_pointers_enabled') == 'True')
    checkbox_shorten_threes.setChecked(parser.get('settings', 'shorten_three_pointers_enabled') == 'True')
    txt_shortened_threes_length.setDisabled(parser.get('settings', 'shorten_three_pointers_enabled') == 'False')
    txt_shortened_threes_length.setText(parser.get('settings', 'shortened_three_pointer_length'))
    checkbox_override_period_length.setChecked(parser.get('settings', 'override_period_length_enabled') == 'True')
    txt_override_period_length.setDisabled(parser.get('settings', 'override_period_length_enabled') == 'False')
    txt_override_period_length.setText(parser.get('settings', 'period_length'))
    apply_clicked()

    if checkbox_disable_threes.isChecked():
        checkbox_shorten_threes.setChecked(False)
        checkbox_shorten_threes.setDisabled(True)

    btn_apply = QtWidgets.QPushButton(win)
    btn_apply.setText("Apply")
    btn_apply.clicked.connect(apply_clicked)
    btn_apply.move(230, 610)

    thread1 = QThread1()
    thread1.start()

    win.show()
    
    ret = app.exec_()
    sys.exit(ret)

window()