import csv, argparse
import pandas as pd
from struct import unpack
from copy import deepcopy
from argparse import Namespace
import cantools
from pprint import pprint, _safe_key

pd.set_option('display.expand_frame_repr', False)
pd.set_option('precision', 8)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

if __name__ == "__main__":

parser = argparse.ArgumentParser(description='CANDUMP to CSV converter')
parser.add_argument('-f', action="store", dest="fileName", help="input file CSV, format: (time), can interface, msgid, data")
results = parser.parse_args()

filename = results.fileName
filename = "candump_log_new"
f = open(filename, 'r')
reader = csv.reader(f, delimiter=' ')

print ('time, intrface, msg id, data')

can_messages = []
for line in reader:
    line = [x for x in line if len(x) > 0]
    can_message = Namespace()
    can_message.timestamp = line[0][1:-1]
    can_message.can_id = line[2]
    can_message.data_length = line[3][1:-1]
    can_message.data = line[4:]
    can_messages.append(can_message)

df = pd.DataFrame([list(x.__dict__.values()) for x in can_messages],
                  columns=list(can_message.__dict__.keys()))

df["data_str"] = df["data"].apply(lambda x: "".join(x))
for msg in can_messages:
    if msg.can_id == "0C7":
        print(msg.data)
        raw_data = unpack('BBBBBBBB', "".join(msg.data[:4]))
        # fan_speed = raw_data[1] / 4
        # driver_temp = parse_temperature(raw_data[2:4])
        # passenger_temp = parse_temperature(raw_data[4:6])

steering = df[df["can_id"] == "0C6"]
speed_kps = df[df["can_id"] == "29C"]
break_pressure = df[df["can_id"] == "090"]

# -- decode
import glob
import numpy as np

dbcs = glob.glob("dbc/*.dbc")
steering_data = steering.data_str.unique()
speed_kps_data = speed_kps.data_str.unique()
break_pressure_data = break_pressure.data_str.values
dbc_file = 'logan.dbc'
cmd_name = "STEERING_SENSORS"
cmd_name = "SPEED_SENSOR"
cmd_name = "BRAKE_SENSOR"

cnt_decode = 1000

for dbc_file in dbcs:
    print("=" * 80)
    print(f"DBC FILE: {dbc_file}")
    try:
        db  = cantools.database.load_file(dbc_file, strict=False)
        db.decode_message(cmd_name, bytearray.fromhex(steering_data[i]))
    except Exception as e:
        continue

    # db.messages

    for db_message in db.messages:
        cmd_name = db_message.name
        # cmd_name = "IO_DEBUG"
        signals = db.get_message_by_name(cmd_name).signals
        any_name = ["angle" in x.name.lower() for x in signals]
        if not np.any(any_name):
            continue

        # example_message = db.get_message_by_name('MOTOR_STATUS')
        # pprint(example_message.signals)
        #
        all_d = []
        for i in range(cnt_decode):
            try:
                d = db.decode_message(cmd_name, bytes.fromhex(steering_data[i]))
                all_d.append(d)
                print(d)
            except Exception as e:
                print("error")

        # print(pd.DataFrame(all_d))
        input()

from matplotlib import pyplot as plt


import re

def replace(file, pattern, subst):
    # Read contents from file as a single string
    file_handle = open(file, 'r')
    file_string = file_handle.read()
    file_handle.close()

    # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
    file_string = (re.sub(pattern, subst, file_string))

    # Write contents to file.
    # Using mode 'w' truncates the file.
    file_handle = open(file+"_change", 'w')
    file_handle.write(file_string)
    file_handle.close()
    return file+"_change"

steering_data = steering.data_str.values

# plt_data = steering_data
# plt_data = speed_kps_data
plt_data = break_pressure_data
change_with = ["@1+"]#, "@1-", "@0+", "@0-"]
fig, ax = plt.subplots(len(change_with))
for ix, ch in enumerate(change_with):
    changed_file = replace(dbc_file, "@1\+", ch)
    # db = cantools.database.load_file(dbc_file, strict=False)
    v = []
    db  = cantools.database.load_file(changed_file, strict=False)
    for i in range(0, len(plt_data), 1):
        new_v = db.decode_message(cmd_name, bytearray.fromhex(plt_data[i]))
        v.append(new_v["PRESIUNE_C_P"])
        # v.append(int(plt_data[i][0:2], 8))
        # print(new_v)
    ax.plot(v)
    print(len(np.unique(v)))

# plt.plot(v)
# plt.show()

plt.plot(v)
plt.show()

DBC FILE: dbc/chrysler_pacifica_2017_hybrid.dbc
DBC FILE: dbc/subaru_outback_2016_eyesight.dbc


for v in steering.data_str.values[800:]:
    print(v)


    def HexToByte(hexStr):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
        # The list comprehension implementation is fractionally slower in this case
        #
        #    hexStr = ''.join( hexStr.split(" ") )
        #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
        #                                   for i in range(0, len( hexStr ), 2) ] )

        bytes = []

        hexStr = ''.join(hexStr.split(" "))

        for i in range(0, len(hexStr), 2):
            bytes.append(chr(int(hexStr[i:i + 2], 16)))

        return ''.join(bytes)
