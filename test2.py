import sys
import obd
import time

stop = False


def new_rpm(r):
    global stop
    if not r.is_null():
        value = r.value.magnitude
        stop = False
    else:
        value = 0
        stop = True
    print(value)
    sys.stdout.flush()
    time.sleep(0.3)


def new_speed(r):
    if not r.is_null():
        value = r.value.magnitude
    else:
        value = 0
    print(value)
    sys.stdout.flush()
    time.sleep(0.3)


def connect():
    print("connecting")
    global connection
    connection = obd.Async("/dev/rfcomm1", fast=False)
    # connection.watch(obd.commands.RPM, callback=new_rpm, force=True)
    # connection.watch(obd.commands.SPEED, callback=new_speed, force=True)
    connection.watch(obd.commands.SPEED, callback=new_speed, force=True)
    connection.start()


connect()

while True:
    if stop == False:
        time.sleep(1)
    else:
        connection.stop()
        connection.unwatch_all()
        stop = False
        connect()