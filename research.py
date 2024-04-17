from pymem import *
import pymem.process as process
import random
import time

#try:
mem = Pymem("nba2k14.exe")
module = process.module_from_name(mem.process_handle, "nba2k14.exe").lpBaseOfDll
going_in = 0
active_shot = False

while True:
    mem.write_float(module + 0x1A1A29C, 5.0)
# print("start.")
""" while True:
    if mem.read_short(module + 0x19EE8F8) == 1 and active_shot == False:
        active_shot = True
        if random.randint(0, 1) == 1:
            going_in = 1
            print("make")
        else:
            going_in = 0
            print("miss")
    if mem.read_short(module + 0x19EE8F8) == 0:
        active_shot = False
    mem.write_short(module + 0x1A165C8, going_in)
    #mem.write_float(module + 0x1A16298, 0.95)
"""
# count = 0

# def possession_based_scoring():
#     print("running...")
#     if mem.read_bool(module + 0x10F5655):
#         mem.write_bool(module + 0x1A165C8, False)
#     else:
#         mem.write_bool(module + 0x1A165C8, True)

# while True:
#     mem.write_float(module + 0x19ACD88, 2)
    #possession_based_scoring()
    #print(mem.read_bool(module + 0x10F5655))
    #print(mem.read_bool(module + 0x1A165C8))
    #print(mem.read_bool(module + 0x1A165C8))
    #print(mem.read_bool(module + 0x1A09A14))
    #print(mem.read_bool(module + 0x1A09924))
    #mem.write_bool(module + 0x1A09A14, False)
    #mem.write_bool(module + 0x1A09924, False)
    #mem.write_bool(module + 0x1A165C8, True)
    #if mem.read_short(module + 0x19C61DC) == 3:
    #mem.write_int(module + 0x1A1629C, 645) ### SHOT ARC!!!! ~ min: 650
    # if mem.read_short(module + 0x19C61DC) == 3 and count < 25:
    #     mem.write_bool(module + 0x1A165C8, True)
    #     mem.write_bool(module + 0x1A09A14, True)
    #     mem.write_bool(module + 0x1A09924, True)
    #     count += 1
    #     print("overwrite...", count)
    # elif mem.read_short(module + 0x19C61DC) != 3:
    #     count = 0
    
    # pretending we're looking at logo of court
    # 0x1A16280 - y-coord, 0 = middle of court, < 0 = south of logo, > 0 north of logo 
    # 0x1A16288 - x-coord, 0 = halfcourt line, < 0 = left side of court, > 0 = right side of court
    #mem.write_float(module + 0x1A16280, 257.92)
    #mem.write_float(module + 0x1A16288, 881.71) """
""" while True:
    if mem.read_short(module + 0x19C61DC) == 3:
        mem.write_bool(module + 0x1A165C8, True) """
"""
while True:
    
    mem.write_float(module + 0xFBCAC4, 0.99999)
    #mem.write_float(module + 0xADB328, 0.99999)
    mem.write_float(module + 0x1A16298, 0.99999)
    mem.write_float(module + 0x1A1640C, 0.99999)
    mem.write_float(module + 0xF0CA28, 0.99999)
    """
"""
    mem.write_float(module + 0xF322A8, 150.0)
    mem.write_float(module + 0xF322AC, 150.0)
    mem.write_float(module + 0xF322EC, 150.0)
    mem.write_float(module + 0xF32320, 150.0)
    mem.write_float(module + 0xF324D8, 150.0)
    mem.write_float(module + 0xF324DC, 150.0)
    mem.write_float(module + 0xF3251C, 150.0)
    mem.write_float(module + 0xF32550, 150.0)
    mem.write_float(module + 0x10F4458, 150.0)
    mem.write_float(module + 0x10F445C, 150.0)
    mem.write_float(module + 0x10F449C, 150.0)
    mem.write_float(module + 0x10F44D0, 150.0)
    mem.write_float(module + 0x1A85928, 150.0)
    mem.write_float(module + 0x1A8592C, 150.0)
    mem.write_float(module + 0x1A8596C, 150.0)
    mem.write_float(module + 0x1A859A0, 150.0)
    mem.write_float(module + 0x1C21338, 150.0)
    mem.write_float(module + 0x1C2133C, 150.0)
    mem.write_float(module + 0x1C2137C, 150.0)
    mem.write_float(module + 0x1C213B0, 150.0)
    mem.write_float(module + 0x1C230B8, 150.0)
    mem.write_float(module + 0x1C230BC, 150.0)
    mem.write_float(module + 0x1C230FC, 150.0)
    mem.write_float(module + 0x1C23130, 150.0)
    """
"""
    mem.write_short(module + 0xD973EB, 68)
    mem.write_short(module + 0x18BD50F, 68)
    #mem.write_short(module + 0x18BD517, 68)
    mem.write_short(module + 0x18BD5AB, 68)
    ###
    mem.write_short(module + 0x18CA28B, 68)
    mem.write_short(module + 0x18CA2AB, 68)
    mem.write_short(module + 0x18CA2CB, 68)
    mem.write_short(module + 0x18CA2EB, 68)
    mem.write_short(module + 0x18CA30B, 68)
    mem.write_short(module + 0x18CA32B, 68)
    mem.write_short(module + 0x18CA34B, 68)
    mem.write_short(module + 0x18CA36B, 68)
    mem.write_short(module + 0x18CA38B, 68)
    mem.write_short(module + 0x18CA3AB, 68)
    mem.write_short(module + 0x18CA3CB, 68)
    mem.write_short(module + 0x18CA3EB, 68)
    mem.write_short(module + 0x18CA40B, 68)
    mem.write_short(module + 0x18CA42B, 68)
    mem.write_short(module + 0x18CA44B, 68)
    ###
    mem.write_short(module + 0x18CA46B, 68)
    mem.write_short(module + 0x18CA48B, 68)
    mem.write_short(module + 0x18CA4AB, 68)
    mem.write_short(module + 0x18CA4CB, 68)
    mem.write_short(module + 0x18CA4EB, 68)
    mem.write_short(module + 0x18CA50B, 68)
    mem.write_short(module + 0x18CA52B, 68)
    mem.write_short(module + 0x18CA54B, 68)
    mem.write_short(module + 0x18CA56B, 68)
    mem.write_short(module + 0x18CA58B, 68)
    mem.write_short(module + 0x18DDB0B, 68)
    mem.write_short(module + 0x18DDB1B, 68)
    mem.write_short(module + 0x18DDB2B, 68)
    mem.write_short(module + 0x18DDB3B, 68)
    ###
    mem.write_short(module + 0x18DDB4B, 68)
    mem.write_short(module + 0x18DDB5B, 68)
    mem.write_short(module + 0x18DDB6B, 68)
    mem.write_short(module + 0x18DDB8B, 68)
    mem.write_short(module + 0x18DDB7B, 68)
    mem.write_short(module + 0x18DDB9B, 68)
    mem.write_short(module + 0x18DDBAB, 68)
    mem.write_short(module + 0x18DDBBB, 68)
    mem.write_short(module + 0x18DDBCB, 68)
    mem.write_short(module + 0x18DDBDB, 68)
    mem.write_short(module + 0x18DDBEB, 68)
    mem.write_short(module + 0x18DDBFB, 68)
    mem.write_short(module + 0x18DDC0B, 68)
    ###
    mem.write_short(module + 0x18DDC1B, 68)
    mem.write_short(module + 0x18DDC2B, 68)
    mem.write_short(module + 0x18DDC3B, 68)
    mem.write_short(module + 0x18DDC4B, 68)
    mem.write_short(module + 0x18DDC5B, 68)
    mem.write_short(module + 0x18DDC6B, 68)
    mem.write_short(module + 0x18DDC7B, 68)
    mem.write_short(module + 0x18DDC8B, 68)
    mem.write_short(module + 0x199B9EB, 68)
    mem.write_short(module + 0x199B9FB, 68)
    ###
    mem.write_short(module + 0x199BEC6, 24)
    mem.write_short(module + 0x199BEC8, 208)
    mem.write_short(module + 0x199BEC9, 204)
    ###
    mem.write_short(module + 0x199BECA, 204)
    mem.write_short(module + 0x199BECC, 106)
    mem.write_short(module + 0x199BECE, 29)
    mem.write_short(module + 0x199BED0, 236)
    ###
    mem.write_short(module + 0x199BED1, 238)
    mem.write_short(module + 0x199BED2, 110)
    mem.write_short(module + 0x199BEDA, 24)
    mem.write_short(module + 0x199BEDC, 208)
    ###
    mem.write_short(module + 0x199BEDD, 153)
    mem.write_short(module + 0x199BEDE, 153)
    mem.write_short(module + 0x199BEE2, 21)
    mem.write_short(module + 0x199BEE3, 63)
    ###
    
    if mem.read_short(module + 0x18BD517) == 195 or mem.read_short(module + 0x18BD517) == 196:
        mem.write_short(module + 0x18BD517, 67)
        print("overwrite")
    print(mem.read_short(module + 0x18BD517))
    # mem.write_short(module + 0x18BD517, 68)
    ###
    """
    ###
"""
    mem.write_short(module + 0x199BEE4, 0)
    mem.write_short(module + 0x199BEE5, 239)
    mem.write_short(module + 0x199BEE6, 238)
    mem.write_short(module + 0x19F6EDB, 67)
    """
    
    #mem.write_short(module + 0x19F6F0B, 66)
"""
    mem.write_short(module + 0x19F6F3B, 67)
    mem.write_short(module + 0x19F6F4B, 67)
    mem.write_short(module + 0x1A097BB, 62)
    mem.write_short(module + 0x18BD517, 68)
    """
    #mem.write_short(module + 0x1A6CC00, 0)
    #mem.write_float(module + 0x1A16290, 300.0)
    
    #mem.write_int(module + 0x1A1629C, 5000) ### SHOT ARC!!!!
    #mem.write_bool(module + 0x1A165C8, True)
    #mem.write_float(module + 0x1A16298, 0.99)

    #mem.write_int(module + 0x1A162A0, 3000)
    #mem.write_float(module + 0xF322A8, 95.0)
"""
    mem.write_float(module + 0x10F4458, 400.0)
    mem.write_float(module + 0x10F445C, 400.0)
    mem.write_float(module + 0x1C21338, 400.0)
    mem.write_float(module + 0x1C2133C, 400.0)
    mem.write_float(module + 0x1C213B0, 400.0)
    mem.write_float(module + 0x1C230B8, 400.0)
    mem.write_float(module + 0x1C230BC, 400.0)
    mem.write_float(module + 0x1C23130, 400.0)
    """
"""
    
    
"""


#except:
  #  print("no")