import csv, argparse
import pandas as pd
from struct import unpack
from copy import deepcopy
from argparse import Namespace
import cantools
from pprint import pprint, _safe_key
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.expand_frame_repr', False)
pd.set_option('precision', 8)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)


def hex_to_int(s, start_i, end_i, byteorder='big', signed=False):
    return int.from_bytes(bytearray.fromhex(s[start_i:end_i]), byteorder=byteorder, signed=signed)


def read_can_file(can_file_path):
    df_can = pd.read_csv(can_file_path, header=None, delimiter=" ")
    df_can["tp"] = df_can[0].apply(lambda x: float(x[1:-1]))
    df_can["can_id"] = df_can[2].apply(lambda x: x[:x.find("#")])
    df_can["data_str"] = df_can[2].apply(lambda x: x[x.find("#") + 1:])
    return df_can

# CAN file line format <(1533228233.465851) can0 55D#00DD600091C00000>
can_file_path = "/media/andrei/Samsung_T51/nemodrive_data/18_nov/session_1/1542549716_log/can_raw.log"

df_can = read_can_file(can_file_path)

# -- Filter messages
MIN_NO_UNIQUE = 5
msg_type_count = df_can.groupby("can_id")["data_str"].nunique()
variable_messages = msg_type_count[msg_type_count > MIN_NO_UNIQUE]

known_ids = ["0C6", "354", "090"]

can_ids = list(filter(lambda x: x not in known_ids, variable_messages.index))

# =======================================================================
# -- speed file
speed_file_path = "/media/andrei/CE04D7C504D7AF291/nemodrive/obd_read/data/log_0/obd_SPEED.log"
df_speed = pd.read_csv(speed_file_path, header=None)
df_speed["value"] = df_speed[1].apply(lambda x: None if x is None else x.split()[0])
df_speed["value"] = df_speed["value"].apply(lambda x: None if x == "None" else float(x))
df_speed.set_index(0, inplace=True)
no_unique_val = df_speed["value"].nunique()

# RPM file
rpm_file_path = "/media/andrei/CE04D7C504D7AF291/nemodrive/obd_read/data/log_0/obd_RPM.log"
df_rpm = pd.read_csv(rpm_file_path, header=None)
df_rpm["value"] = df_rpm[1].apply(lambda x: None if x is None else x.split()[0])
df_rpm["value"] = df_rpm["value"].apply(lambda x: None if x == "None" else float(x))
df_rpm.set_index(0, inplace=True)
no_unique_val = df_rpm["value"].nunique()

# =======================================================================


# Analyze
same_plot = False
possible_ids = ["217", "29C", "354", "7E8"]
df_other = df_speed
for can_id in possible_ids:
# for can_id in can_ids:
    print("PLOT: {}".format(can_id))
    df_id = df_can[df_can["can_id"] == can_id]
    unique_msg = df_id["data_str"].unique()
    df_id["msg_unique"] = df_id["data_str"].apply(lambda x: np.where(unique_msg == x)[0][0])
    unique_msg_stats = pd.DataFrame([list(x) for x in unique_msg])
    byte_count = unique_msg_stats.nunique()

    # same x
    fig = plt.figure()
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)

    if True:
        ax1.scatter(df_id["tp"], df_id["msg_unique"], s=0.2)
    else:
        # Plot converted version
        transf = df_id["data_str"].apply(lambda x: hex_to_int(x, 0, 4)).values
        ax1.scatter(df_id["tp"], transf, s=0.2)

    # ax2.plot(df_other.index, df_other["value"])
    ax2.scatter(df_other.index, df_other["value"], s=0.2)

    ax1.get_shared_x_axes().join(ax1, ax2)
    ax1.set_xticklabels([])
    # ax2.autoscale() ## call autoscale if needed

    plt.show()

    if same_plot:
        plt.scatter(df_id["tp"], transf, s=0.2)
        plt.scatter(df_other.index, df_other["value"], s=0.2)
        plt.show()

    print("Done {}".format(can_id))
    input()

for x in df_id["data_str"].values:
    print(x)
    input()