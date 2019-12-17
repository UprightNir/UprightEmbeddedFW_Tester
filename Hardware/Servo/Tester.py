import time, os,math,atexit,csv,sys
from Tkinter import *
import Tkinter as tk
from threading import Thread, Lock
import pkgutil
import serial
import module
from tabulate import tabulate
from random import randint

import Arduino
import Btool
import Defines


defines = Defines.Defines()
#  config file name:
config_file_name = 'configGo.txt'

#
#  com ports configuration, BLE and Arduino:
btoolComPort = 'COM4'
arduinoComPort = 'COM9'
NO_LOG = open(os.devnull, 'w')
LOG = sys.stdout


btool = Btool.Btool()
btool.Init()
btool.PrintStat("init")

arduino = Arduino.Arduino()

#=======================================================================================main loop=====================================================================
#  config file open:
config_file = open(config_file_name, 'r')  # read configuration file

#  Log file open:
logfile = open("Log.txt", "w")  # open Log file
root = tk.Tk()
frame = tk.Frame(root)

frame.pack()

arrayCommands = []
Command = False


#  enable output Log
def enableLog():
    sys.stdout = LOG

#  disable output Log
def disableLog():
    sys.stdout = NO_LOG

#  clear the current calibration using Btool command
def uprightClearCalib():
    arduino.FlushInput()
    btool.ClearCalibration()
    arduino.FlushInput()
    return btool.PrintStat("clear calibration")


#  exit program function
def exit_handler():
    print "exiting...."
    btool.Disconnect()
    btool.PrintStat("disconnect")
    time.sleep(defines.Disconnect_time)
    btool.ClosePort()
    arduino.ClosePort()
    logfile.close()
    config_file.close()
    NO_LOG.close()
    print "exit successfully"
atexit.register(exit_handler)




def WaitSec(sec):
    time.sleep(sec)


def BeginOfNewTest():
    global arrayCommands
    arrayCommands = []
    arrayCommands.append('0')
    input = "Begin Of The Test \n"
    Command_1.config(text = str(input))

def EndOfNewTest():
    global arrayCommands
    arrayCommands.append('1')
    input = Command_1.cget("text") + "End Of Test\n"
    Command_1.config(text=str(input))

def ShortPushButton():
    global arrayCommands
    arrayCommands.append('2')
    input = Command_1.cget("text") + "Short Push Button\n"
    Command_1.config(text=str(input))

def LongPushButton():
    global arrayCommands
    arrayCommands.append('3')
    input = Command_1.cget("text") + "Long Push Button\n"
    Command_1.config(text=str(input))


def DoublePushButton():
    global arrayCommands
    arrayCommands.append('4')
    input = Command_1.cget("text") + "Double Push Button\n"
    Command_1.config(text=str(input))

def GATTCalibration():
    global arrayCommands
    arrayCommands.append('5')
    input = Command_1.cget("text") + "GATT calibration\n"
    Command_1.config(text=str(input))


def ConnectToBtool():
    global arrayCommands
    arrayCommands.append('6')
    input = Command_1.cget("text") + "Connect to Btool\n"
    Command_1.config(text=str(input))

def DisConnectToBtool():
    global arrayCommands
    arrayCommands.append('7')
    input = Command_1.cget("text") + "Disconnect from Btool \n"
    Command_1.config(text=str(input))

def MoveToVibrationOn():
    global arrayCommands
    arrayCommands.append('8')
    input = Command_1.cget("text") + "Move to vibration ON by GATT command \n"
    Command_1.config(text=str(input))


def MoveToVibrationOff():
    global arrayCommands
    arrayCommands.append('9')
    input = Command_1.cget("text") + "Move to vibration OFF by GATT command \n"
    Command_1.config(text=str(input))


def WaitSeconds():
    global arrayCommands
    arrayCommands.append('12')
    arrayCommands.append(waitSec.get())
    input = Command_1.cget("text") + "Wait Seconds " + waitSec.get() + "\n"
    Command_1.config(text=str(input))


def MoveSpecificAngle():
    global arrayCommands
    arrayCommands.append('14')
    arrayCommands.append(angle.get())
    input = Command_1.cget("text") + "Move to Angle " + angle.get() + "\n"
    Command_1.config(text=str(input))

def ShutDownByGATTCommand():
    global arrayCommands
    arrayCommands.append('15')
    input = Command_1.cget("text") + "Shutdown By GATT command \n"
    Command_1.config(text=str(input))

def RunTheTest():
    currAngle = 0
    isConnected = False
    testStatus = defines.PASS
    print "start reading file"
    instruction = csv.reader(config_file)
    time.sleep(0.2)
    # btool.resetConnection()
    TestNumCount = 0
    i = 0
    print "Array commands len:"
    print len(arrayCommands)
    print arrayCommands
    # for row in instruction:
    #     print row



    print arrayCommands
    if '0' == arrayCommands[0] and '1' == arrayCommands[arrayCommands.__len__() - 1]: # if the scenario doesnt include both 0 - start and 1 - Finish
        print "Starting Test :" + str(TestNumCount) + "\n"
        logfile.write("Start Scenario :" + str(TestNumCount) + "\n")
        print len(arrayCommands)
        while i < len(arrayCommands):
            i = i + 1
            # print row[i]
            if ('1' == arrayCommands[i]) or (testStatus == defines.FAIL):  # End of the test
                logfile.write("End Of Scenario :" + str(TestNumCount) + "\n")
                if testStatus == defines.PASS:
                    logfile.write("Result of Scenario :" + str(TestNumCount) + "-> Pass")
                    print testStatus
                    # Print to file PASS
                else:
                    logfile.write(str(TestNumCount) + "\t" + "Fail")
                    print testStatus

                TestNumCount = TestNumCount + 1
                i = 0
                testStatus = defines.PASS
                break

            elif '2' == arrayCommands[i]:  # Power On
                logfile.write("Short Push Button " + "\n")
                arduino.ShortPushButton()

            elif '3' == arrayCommands[i]:  # Power Off
                logfile.write("Long Push Button " + "\n")
                arduino.LongPushButton()
                isConnected = False

            elif '4' == arrayCommands[i]:  # calib - manually with waiting
                logfile.write("Double Push button" + "\n")
                arduino.DoublePushButton(currAngle)

            elif '5' == arrayCommands[i]:  # calib - Btool with waiting
                logfile.write("GATT calibration" + "\n")
                testStatus = btool.BtoolClaibWait(arduino)

            elif '6' == arrayCommands[i]:  # Connect to Upright
                logfile.write("Connect to btool" + "\n")
                btool.ConnectToUpright()
                isConnected = True

            elif '7' == arrayCommands[i]:  # DisConnect from Upright
                logfile.write("disConnect from btool" + "\n")
                btool.Disconnect()
                isConnected = False

            elif '8' == arrayCommands[i]:  # Move to Train via btool
                logfile.write("Move to vibration ON by GATT command" + "\n")
                testStatus = btool.MoveToTraining()

            elif '9' == arrayCommands[i]:  # Move To Track via btool
                logfile.write("Move to vibration OFF by GATT command" + "\n")
                testStatus = btool.MoveToTracking()

            elif '10' == arrayCommands[i]:  # Move to Train Manually
                logfile.write("Move to vibration ON by Push button" + "\n")
                arduino.MoveToTrainManual()

            elif '11' == arrayCommands[i]:  # Move to Track Manually
                logfile.write("Move to vibration OFF by Push button" + "\n")
                arduino.MoveToTrackManual()

            elif '12' == arrayCommands[i]:
                logfile.write("Wait " + arrayCommands[i + 1] + "\n")
                WaitSec(int(arrayCommands[i + 1]))  # Wait for a specific amount of time(seconds) casting needed for the time.sleep function.
                i = i + 1

            elif '13' == arrayCommands[i]:
                logfile.write("Read Online Data and Verify expected data" + "\n")
                testStatus = btool.ReadOnlineData(arrayCommands[i + 1], arrayCommands[i + 2], arrayCommands[i + 3], arrayCommands[i + 4],
                                                  arrayCommands[i + 5])  # This is only for the first byte in online data
                i = i + 4

            elif '14' == arrayCommands[i]:  # Move to specific angle
                logfile.write("Move to Angle : " + arrayCommands[i + 1] + "\n")
                arduino.MoveToSpecificAngle(arrayCommands[i + 1])
                time.sleep(2)
                currAngle = int(arrayCommands[i + 1])
                i = i + 1

            elif '15' == arrayCommands[i]:
                logfile.write("ShutDown by GATT command" + "\n")
                btool.ShutDownDevice()
                isConnected = False

            elif '16' == arrayCommands[i]:
                logfile.write("DeepSleep by GATT command" + "\n")
                btool.DeepSleepDevice()
                isConnected = False

            elif '17' == arrayCommands[i]:
                logfile.write("Change FreeStyle Range to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeFreeStyleRange(arrayCommands[i + 1])
                i = i + 1

            elif '18' == arrayCommands[i]:
                logfile.write("Change Train Range to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeTrainRange(arrayCommands[i + 1])
                i = i + 1

            elif '19' == arrayCommands[i]:
                logfile.write("Change FreeStyle Delay to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeFreeStyleDelay(arrayCommands[i + 1])
                i = i + 1

            elif '20' == arrayCommands[i]:
                logfile.write("Change Train Delay to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeTrainDelay(arrayCommands[i + 1])
                i = i + 1

            elif '21' == arrayCommands[i]:
                logfile.write("Change FreeStyle Pattern to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeFreestylePattern(arrayCommands[i + 1])
                i = i + 1

            elif '22' == arrayCommands[i]:
                logfile.write("Change Train Pattern to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeTrainPattern(arrayCommands[i + 1])
                i = i + 1

            elif '23' == arrayCommands[i]:
                logfile.write("Change FreeStyle Strength to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeFreeStyleStrength(arrayCommands[i + 1])
                i = i + 1

            elif '24' == arrayCommands[i]:
                logfile.write("Change Train Strength to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeTrainStrength(arrayCommands[i + 1])
                i = i + 1

            elif '25' == arrayCommands[i]:
                logfile.write("Change FreeStyle Periods to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeFreeStylePeriods(arrayCommands[i + 1])
                i = i + 1

            elif '26' == arrayCommands[i]:
                logfile.write("Change Train Periods to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeTrainPeriods(arrayCommands[i + 1])
                i = i + 1

            elif '27' == arrayCommands[i]:
                logfile.write("Change FreeStyle Stop seconds to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeFreeStyleStopSec(arrayCommands[i + 1])
                i = i + 1

            elif '28' == arrayCommands[i]:
                logfile.write("Change Train Stop seconds to :" + arrayCommands[i + 1] + "\n")
                testStatus = btool.ChangeTrainStopSec(arrayCommands[i + 1])
                i = i + 1

            elif '29' == arrayCommands[i]:
                logfile.write("Read Angle Value" + "\n")
                time.sleep(3)
                testStatus = btool.ReadAngle(currAngle)


            elif '30' == arrayCommands[i]:
                logfile.write("Verify Short Vibration On ,Turn On" + "\n")
                testStatus = arduino.VerifyVibShortOn()

            elif '31' == arrayCommands[i]:
                logfile.write("Verify Short Vibration On ,Turn Off" + "\n")
                testStatus = arduino.VerifyVibShortOff()

            elif '32' == arrayCommands[i]:
                logfile.write("Verify Manual calibration push" + "\n")
                testStatus = arduino.VerifyManualCalibration(btool, isConnected)

    else:
        for row in instruction:
            print row
            if '0' == row[0]:
                print "Starting Test :" + str(TestNumCount) + "\n"
                logfile.write("Start Scenario :" + str(TestNumCount) + "\n")
                print len(row)
                while i < len(row):
                    i = i + 1
                    # print row[i]
                    if ('1' == row[i]) or (testStatus == defines.FAIL):  # End of the test
                        logfile.write("End Of Scenario :" + str(TestNumCount) + "\n")
                        if testStatus == defines.PASS:
                            logfile.write("Result of Scenario :" + str(TestNumCount) + "-> Pass")
                            print testStatus
                            # Print to file PASS
                        else:
                            logfile.write(str(TestNumCount) + "\t" + "Fail")
                            print testStatus

                        TestNumCount = TestNumCount + 1
                        i = 0
                        testStatus = defines.PASS
                        break

                    elif '2' == row[i]:  # Power On
                        logfile.write("Short Push Button " + "\n")
                        arduino.ShortPushButton()

                    elif '3' == row[i]:  # Power Off
                        logfile.write("Long Push Button " + "\n")
                        arduino.LongPushButton()
                        isConnected = False

                    elif '4' == row[i]:  # calib - manually with waiting
                        logfile.write("Double Push button" + "\n")
                        arduino.DoublePushButton(currAngle)

                    elif '5' == row[i]:  # calib - Btool with waiting
                        logfile.write("GATT calibration" + "\n")
                        testStatus = btool.BtoolClaibWait(arduino)

                    elif '6' == row[i]:  # Connect to Upright
                        logfile.write("Connect to btool" + "\n")
                        btool.ConnectToUpright()
                        isConnected = True

                    elif '7' == row[i]:  # DisConnect from Upright
                        logfile.write("disConnect from btool" + "\n")
                        btool.Disconnect()
                        isConnected = False

                    elif '8' == row[i]:  # Move to Train via btool
                        logfile.write("Move to vibration ON by GATT command" + "\n")
                        testStatus = btool.MoveToTraining()

                    elif '9' == row[i]:  # Move To Track via btool
                        logfile.write("Move to vibration OFF by GATT command" + "\n")
                        testStatus = btool.MoveToTracking()

                    elif '10' == row[i]:  # Move to Train Manually
                        logfile.write("Move to vibration ON by Push button" + "\n")
                        arduino.MoveToTrainManual()

                    elif '11' == row[i]:  # Move to Track Manually
                        logfile.write("Move to vibration OFF by Push button" + "\n")
                        arduino.MoveToTrackManual()

                    elif '12' == row[i]:
                        logfile.write("Wait " + row[i + 1] + "\n")
                        WaitSec(int(row[
                                        i + 1]))  # Wait for a specific amount of time(seconds) casting needed for the time.sleep function.
                    elif '13' == row[i]:
                        logfile.write("Read Online Data and Verify expected data" + "\n")
                        testStatus = btool.ReadOnlineData(row[i + 1], row[i + 2], row[i + 3], row[i + 4],
                                                          row[i + 5])  # This is only for the first byte in online data
                        i = i + 4
                    elif '14' == row[i]:# Move to specific angle
                        logfile.write("Move to Angle : " + row[i + 1] + "\n")
                        arduino.MoveToSpecificAngle(row[i + 1])
                        currAngle = int(row[i + 1])
                        i = i + 1

                    elif '15' == row[i]:
                        logfile.write("ShutDown by GATT command" + "\n")
                        btool.ShutDownDevice()
                        isConnected = False

                    elif '16' == row[i]:
                        logfile.write("DeepSleep by GATT command" + "\n")
                        btool.DeepSleepDevice()
                        isConnected = False

                    elif '17' == row[i]:
                        logfile.write("Change FreeStyle Range to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeFreeStyleRange(row[i + 1])
                        i = i + 1

                    elif '18' == row[i]:
                        logfile.write("Change Train Range to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeTrainRange(row[i + 1])
                        i = i + 1

                    elif '19' == row[i]:
                        logfile.write("Change FreeStyle Delay to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeFreeStyleDelay(row[i + 1])
                        i = i + 1

                    elif '20' == row[i]:
                        logfile.write("Change Train Delay to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeTrainDelay(row[i + 1])
                        i = i + 1

                    elif '21' == row[i]:
                        logfile.write("Change FreeStyle Pattern to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeFreestylePattern(row[i + 1])
                        i = i + 1

                    elif '22' == row[i]:
                        logfile.write("Change Train Pattern to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeTrainPattern(row[i + 1])
                        i = i + 1

                    elif '23' == row[i]:
                        logfile.write("Change FreeStyle Strength to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeFreeStyleStrength(row[i + 1])
                        i = i + 1

                    elif '24' == row[i]:
                        logfile.write("Change Train Strength to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeTrainStrength(row[i + 1])
                        i = i + 1

                    elif '25' == row[i]:
                        logfile.write("Change FreeStyle Periods to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeFreeStylePeriods(row[i + 1])
                        i = i + 1

                    elif '26' == row[i]:
                        logfile.write("Change Train Periods to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeTrainPeriods(row[i + 1])
                        i = i + 1

                    elif '27' == row[i]:
                        logfile.write("Change FreeStyle Stop seconds to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeFreeStyleStopSec(row[i + 1])
                        i = i + 1

                    elif '28' == row[i]:
                        logfile.write("Change Train Stop seconds to :" + row[i + 1] + "\n")
                        testStatus = btool.ChangeTrainStopSec(row[i + 1])
                        i = i + 1

                    elif '29' == row[i]:
                        logfile.write("Read Angle Value" + "\n")
                        testStatus = btool.ReadAngle(currAngle)

                    elif '30' == row[i]:
                        logfile.write("Verify Short Vibration On ,Turn On" + "\n")
                        testStatus = arduino.VerifyVibShortOn()

                    elif '31' == row[i]:
                        logfile.write("Verify Short Vibration On ,Turn Off" + "\n")
                        testStatus = arduino.VerifyVibShortOff()

                    elif '32' == row[i]:
                        logfile.write("Verify Manual calibration push" + "\n")
                        testStatus = arduino.VerifyManualCalibration(btool, isConnected)


bBegin = Button(frame, text="Begin New Test", command=BeginOfNewTest)
bBegin.pack()

# Marks the End of the test
bEnd = Button(frame, text="End Test", command=EndOfNewTest)
bEnd.pack()

# Short Push Button
bShortPushButton = Button(frame, text="Short Push button", command=ShortPushButton)
bShortPushButton.pack()

# Long Push Button
bLongPushButton = Button(frame, text="Long Push button", command=LongPushButton)
bLongPushButton.pack()

# Double Push Button
bLongPushButton = Button(frame, text="Double Push button", command=DoublePushButton)
bLongPushButton.pack()

# GATT calibration
bGATTCalibration = Button(frame, text="GATT Calibration", command=GATTCalibration)
bGATTCalibration.pack()

# Connect to Btool
bConnectToBtool = Button(frame, text="Connect To Btool", command=ConnectToBtool)
bConnectToBtool.pack()

# Disconnect to Btool
bDisConnectToBtool = Button(frame, text="DisConnect To Btool", command=DisConnectToBtool )
bDisConnectToBtool.pack()

# Move to Vibration ON with GATT command
bMoveToVibrationOn = Button(frame, text="Move To Vibration On", command=MoveToVibrationOn)
bMoveToVibrationOn.pack()

# Move to Vibration OFF with GATT command
bMoveToVibrationOff = Button(frame, text="Move To Vibration Off", command=MoveToVibrationOff)
bMoveToVibrationOff.pack()

#Move to Angle X
bMoveToSpecificAngle = Button(frame, text="Move to specific Angle", command=MoveSpecificAngle)
bMoveToSpecificAngle.pack()
angle = StringVar()
AngleEntry = Entry(frame, textvariable=angle)
AngleEntry.pack()

# WaitSeconds
bWaitSeconds= Button(frame, text="Wait for X seconds", command=WaitSeconds)
bWaitSeconds.pack()
waitSec = StringVar()
SecEntry = Entry(frame, textvariable=waitSec)
SecEntry.pack()



bShutDownByGATT = Button(frame, text="Send Shutdown Command via Btool", command=ShutDownByGATTCommand)
bShutDownByGATT.pack()

bRun = Button(frame, text="Run The Test", command=RunTheTest)
bRun.pack()


Command_1 = tk.Label(frame, fg="dark green")
Command_1.pack()


#  main
#  btool com port init

def main():
    root.mainloop()


if __name__ == '__main__':
    main()








