import sys
import obd
import time
import obd
from obd import OBDCommand, ECU


def angle(messages):
    """ decoder for angle messages """
    print(messages[0].data)
    return 0

connection = obd.OBD() # auto-connects to USB or RF port
obd.scan_serial()
cmd = obd.commands.SPEED # select an OBD command (sensor)

cmd = OBDCommand("Angle",
                 "Steering Wheel Angle",
                 b"2147",
                 0,
                 angle,
                 ECU.ALL,
                 False)

connection.supported_commands.add(cmd)
connection.query(cmd)
