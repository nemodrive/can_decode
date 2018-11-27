import matplotlib.pyplot as plt
import cantools
import pandas as pd
import cv2
import numpy as np

LOG_FOLDER = "/media/andrei/Seagate Expansion Drive/nemodrive/1539434900_log/"
CAN_FILE_PATH = LOG_FOLDER + "can_raw.log"
DBC_FILE = "logan.dbc"
SPEED_CAN_ID = "354"
OBD_SPEED_FILE = LOG_FOLDER + "obd_SPEED.log"
CAMERA_FILE_PREFIX = LOG_FOLDER + "small_1_cut"


def read_can_file(can_file_path):
    df_can = pd.read_csv(can_file_path, header=None, delimiter=" ")
    df_can["tp"] = df_can[0].apply(lambda x: float(x[1:-1]))
    df_can["can_id"] = df_can[2].apply(lambda x: x[:x.find("#")])
    df_can["data_str"] = df_can[2].apply(lambda x: x[x.find("#") + 1:])
    return df_can


def get_can_data(db, cmd, data, msg):
    decoded_info = db.decode_message(cmd, bytearray.fromhex(msg))
    return decoded_info[data]


# =======================================================================
# -- Load DBC file stuff

db = cantools.database.load_file(DBC_FILE, strict=False)

cmd_name = "SPEED_SENSOR"
data_name = "SPEED_KPS"

"""
    Decode values using: 
    Define: cmd_name, data_name, raw_can_msg
    
    decoded_info = db.decode_message(cmd_name, bytearray.fromhex(raw_can_msg))
    print(decoded_info[data_name])
ffmpeg -f v4l2 -video_size {}x{} -i /dev/video{} -c copy {}.mkv
"""

# =======================================================================
# -- Load Raw can

df_can = read_can_file("/media/andrei/Seagate Expansion Drive/nemodrive/1533228223_log/can_raw.log")

# =======================================================================
# -- Load speed command

df_can_speed = df_can[df_can["can_id"] == SPEED_CAN_ID]

df_can_speed["speed"] = df_can_speed["data_str"].apply(lambda x: get_can_data(db, cmd_name,
                                                                              data_name, x))

df_can_speed[df_can_speed.speed > 0]
df_can_speed["pts"] = df_can_speed["tp"] - 1539434950.220346

# =======================================================================
# -- Load steer command

STEER_CMD_NAME = "STEERING_SENSORS"
STEER_CMD_DATA_NAME = "STEER_ANGLE"
STEERING_CAN_ID = "0C6"

df_can_steer = df_can[df_can["can_id"] == STEERING_CAN_ID]

df_can_steer["steering"] = df_can_steer["data_str"].apply(lambda x: get_can_data(db,
                                                                                 STEER_CMD_NAME,
                                                                                 STEER_CMD_DATA_NAME, x))
# --Plot can data
plt.plot(df_can_steer["tp"].values, df_can_steer["steering"])

plt.show()

steering_values = []
rng = 100
for index in range(rng, len(df_can_steer)):
    x = df_can_steer.iloc[index-rng: index+1]["steering"].values
    steering_values.append(np.abs(x[1:] - x[:-1]).sum())

steering_values_df = pd.Series(steering_values[:36494], name="Steering angle per second")
steering_values_df.describe()
# steering_values_df.plot()
steering_values_df.plot(kind="box")
plt.show()


# =======================================================================
# -- speed file
df_speed = pd.read_csv(OBD_SPEED_FILE, header=None)
df_speed["value"] = df_speed[1].apply(lambda x: None if x is None else x.split()[0])
df_speed["value"] = df_speed["value"].apply(lambda x: None if x == "None" else float(x))
df_speed.set_index(0, inplace=True)
no_unique_val = df_speed["value"].nunique()

# =======================================================================
# --Plot can data
plt.plot(df_can_speed["tp"].values, df_can_speed["speed"])

# Plot
plt.plot(df_speed.index, df_speed["value"].values)

plt.show()

# =======================================================================
# -- CAMERA processing

camera_start_tp = None
with open(CAMERA_FILE_PREFIX + "_timestamp") as file:
    data = file.read()
    camera_start_tp = float(data)

camera_start_tp = 1539434950.130855 - 35.4

pts_file = pd.read_csv(CAMERA_FILE_PREFIX + "_pts.log", header=None)
pts_file["tp"] = pts_file[0] + camera_start_tp

# search for each frame the closest speed info
camera_speed = pts_file.copy()
camera_speed["speed"] = -1.0
camera_speed["dif_tp"] = -333.

pos_can = 0

v = []
prev = 0
for index, row in pts_file.iterrows():
    v.append(row[0] - prev)
    prev = row[0]


for index, row in camera_speed.iterrows():
    frame_tp = row["tp"]
    dif_crt = df_can_speed.iloc[pos_can]["tp"] - frame_tp
    dif_next = df_can_speed.iloc[pos_can+1]["tp"] - frame_tp

    while abs(dif_next) < abs(dif_crt) and pos_can < len(df_can_speed):
        dif_crt = df_can_speed.iloc[pos_can]["tp"] - frame_tp
        dif_next = df_can_speed.iloc[pos_can + 1]["tp"] - frame_tp
        pos_can += 1

    if pos_can >= len(df_can_speed):
        print("reached end of df_can_speed")

    row["speed"] = df_can_speed.iloc[pos_can]["speed"]
    row["dif_tp"] = dif_crt


# Analyze
camera_speed["dif_tp"].describe()

# Write camera speed file
with open(CAMERA_FILE_PREFIX + "_speed.log", 'w') as filehandle:
    for listitem in camera_speed["speed"].values:
        filehandle.write('%.2f\n' % listitem)


# Run video
vid = cv2.VideoCapture(CAMERA_FILE_PREFIX + ".mp4")

for i in range(350):
    ret, frame = vid.read()
i += 1

frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
prev = frame
while True:
    i += 1
    print(i)
    ret, frame = vid.read()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Test", frame-prev)
    cv2.imshow("Test", frame)
    prev = frame
    cv2.waitKey(0)


frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
prev = frame

while True:
    i += 1
    print(f"Frame:{i}_speed:{camera_speed.loc[i]['speed']}")
    ret, frame = vid.read()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # image = frame-prev
    # show = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    show = frame
    cv2.putText(show, f"{camera_speed.loc[i]['speed']}", (250, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 200), 4)
    cv2.imshow("Test", show)
    prev = frame
    cv2.waitKey(0)





