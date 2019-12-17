import serial
import Commands
import time
import Defines
import Arduino

class Btool:
    btoolComPort = 'COM4'
    commands = Commands.Commands()
    defines = Defines.Defines()
    btSer = serial.Serial(btoolComPort, 115200, timeout=defines.timeout_time)


    def Init(self):
        self.btSer.write_timeout = 5
        self.btSer.write(self.commands.init)
        time.sleep(self.defines.init_time)

    def OpenPort(self):
        self.btSer.open()

    def ClosePort(self):
        self.btSer.close()

    def FlushInput(self):
        self.btSer.flushInput()

    def FlushOutput(self):
        self.btSer.flushOutput()

    def ConnectToUpright(self):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.connect)
        time.sleep(2)
        return self.PrintStat("connect")

    def ReadAngle(self, currAngle):
        self.FlushInput()
        self.FlushOutput()
        time.sleep(2)
        self.btSer.write(self.commands.GetAngle)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.GetAngle)
        time.sleep(2)
        print "send get angle command"
        doubleRes = "Error"
        # read 20 bytes and encode to hex, bytes 18 and 19 represents the angle value in hex:
        hexIn = self.btSer.read(20).encode('hex')
        if hexIn.__len__() < 20:
            return self.defines.FAIL
        res1 = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)][18]  #
        res2 = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)][19]  #
        res = res2 + res1
        intRes = int(res, 16)  # change type from string to int
        doubleRes = float(intRes)  # /10  # divide by 10 to receive the actual angle
        print hexIn
        print res
        print doubleRes/10
        doubleRes = doubleRes / 10
        if currAngle > doubleRes + 5 or currAngle < doubleRes - 5:
            return self.defines.FAIL
        return self.defines.PASS
        #  print hexIn2

    # print point with title
    def PrintStat(self, title):
        time.sleep(2)
        hexIn = self.btSer.read(9).encode('hex')
        if hexIn.__len__() < 9:
            return self.defines.FAIL
        res = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)][5]
        print title, ":", res == '00'
        self.FlushInput()
        return res == '00'

    def ReadOnlineData(self, posture, vibState, movement, sessionMode, countVib):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readOnlineData)
        hexIn = self.btSer.read(31).encode('hex')
        if hexIn.__len__() < 31:
            return self.defines.FAIL
        OnlineData = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        first4Bits = OnlineData[18][0]
        parse = int("0x" + first4Bits + "0", 0) - int('0')
        postureData = (parse & 0x80) >> 7
        vibrationStatus = (parse & 0x40) >> 6
        movement = (parse & 0x30) >> 4
        last4Bits = OnlineData[18][1]
        parse = int("0x0" + last4Bits, 0) - int('0')
        sessionMode = (parse & 0x08) >> 3
        vibCounter = parse & 0x07
        print postureData
        print vibrationStatus
        print sessionMode
        print vibCounter
        # print first4Bits
        print OnlineData
        return True

    def resetConnection(self):
        self.btSer.write(self.commands.disconnect)
        self.PrintStat("disconnect")
        time.sleep(self.defines.Reset_connection_time)
        self.ClosePort()
        self.OpenPort()
        self.btSer.write(self.commands.init)
        self.PrintStat("reset")
        if not self.ConnectToUpright():
            print "fail - unable to connect to upright"

    #  start calib - send calibration command via Btool
    def UprightStartCalib(self):
        self.btSer.write(self.commands.calib)
        return self.PrintStat("calib")

    #Verify moving to vibration On state
    def CheckTrainMode(self):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readVibrationStatus)
        hexIn = self.btSer.read(19).encode('hex')
        if hexIn.__len__() < 19:
            return self.defines.FAIL
        sessionState = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        if sessionState[18] == '00':
            return self.defines.PASS
        return  self.defines.FAIL

    # Verify moving to vibration Off state
    def CheckTrackMode(self):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readVibrationStatus)
        hexIn = self.btSer.read(19).encode('hex')
        if hexIn.__len__() < 19:
            return self.defines.FAIL
        sessionState = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        if sessionState[18] == '01':
            return self.defines.PASS
        return  self.defines.FAIL

    #  Move UPRIGHT to tracking state using Btool command
    def MoveToTracking(self):
        self.btSer.write(self.commands.vibrationOff)
        time.sleep(self.defines.switch_mode_time)
        return self.CheckTrackMode()

    #  Move UPRIGHT to training state using Btool command
    def MoveToTraining(self):
        self.btSer.write(self.commands.vibrationOn)
        time.sleep(self.defines.switch_mode_time)
        return self.CheckTrainMode()

    def ClearCalibration(self):
        self.btSer.write(self.commands.clearCalib)

    def Disconnect(self):
        self.btSer.write(self.commands.disconnect)

    def CheckCalibration(self):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readcalibAckPoints)
        hexIn = self.btSer.read(23).encode('hex')
        if hexIn.__len__() < 23:
            return self.defines.FAIL
        calibAckPoints = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print "calib:"
        print calibAckPoints
        if calibAckPoints[18] == '02':
            return self.defines.PASS
        else:
            return self.defines.FAIL

    def BtoolClaibWait(self,arduino):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.calib)
        time.sleep(2)
        if arduino.waitForCalibrationVib():
            return self.CheckCalibration()
        return self.defines.FAIL
        # Delay until upright finish calibration

    def ShutDownDevice(self):
        self.FlushInput()
        self.FlushOutput()
        time.sleep(1)
        self.btSer.write(self.commands.shutDownDevice)
        hexIn = self.btSer.read(27).encode('hex')
        if hexIn.__len__() < 27:
            return self.defines.FAIL
        terminationAck = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        if terminationAck[26] == '13':
            return self.defines.PASS
        return self.defines.FAIL

    def DeepSleepDevice(self):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.deepSleepDevice)
        hexIn = self.btSer.read(27).encode('hex')
        if hexIn.__len__() < 27:
            return self.defines.FAIL
        terminationAck = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        if terminationAck[26] == '13':
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeValue(self, sessionMode, target):
        print "Todo"

    def ChangeFreeStyleRange(self, Range):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        freeStyleSettings = "0" + Range + tSettings[19] + tSettings[20] + tSettings[21] + tSettings[22] + tSettings[23] + tSettings[24] + tSettings[25]
        #print self.commands.changeFreeStyleRangeValue
        writeRangeCommand = self.commands.changeFreeStyleSettingsValue  + freeStyleSettings.decode('hex')
        self.btSer.write(writeRangeCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings[18][1]
        if tSettings[18][1] == Range:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeTrainRange(self, Range):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        trainSettings = "0" + Range + tSettings[19] + tSettings[20] + tSettings[21] + tSettings[22] + tSettings[23] + \
                        tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writeRangeCommand = self.commands.changeTrainSettingsValue + trainSettings.decode('hex')
        self.btSer.write(writeRangeCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings[18][1]
        if tSettings[18][1] == Range:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeFreeStyleDelay(self,Delay):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        Delay = int(Delay)
        Delay = hex(Delay * 10)
        print Delay
        if Delay.__len__() == 5:
            Delay = Delay[3] + Delay[4] + "0" + Delay[2]
            print Delay
        elif Delay.__len__() == 6:
            Delay = Delay[4] + Delay[5] + Delay[3] + Delay[2]
        else:
            Delay = Delay[2] +  Delay[3] + "0" + "0"
        freeStyleSettings = tSettings[18] + Delay + tSettings[21] + tSettings[22] + tSettings[23] + \
                        tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writeDelayCommand = self.commands.changeFreeStyleSettingsValue + freeStyleSettings.decode('hex')
        self.btSer.write(writeDelayCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        print tSettings[18][1]
        if tSettings[19] + tSettings[20] == Delay:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeTrainDelay(self, Delay):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        Delay = int(Delay)
        Delay = hex(Delay * 10)
        print Delay
        if Delay.__len__() == 5:
            Delay = Delay[3] + Delay[4] + "0" + Delay[2]
            print Delay
        elif Delay.__len__() == 6:
            Delay = Delay[4] + Delay[5] + Delay[3] + Delay[2]
        else:
            Delay = Delay[2] + Delay[3] + "0" + "0"
        trainSettings = tSettings[18] + Delay + tSettings[21] + tSettings[22] + tSettings[23] + \
                            tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writeDelayCommand = self.commands.changeTrainSettingsValue + trainSettings.decode('hex')
        self.btSer.write(writeDelayCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        print tSettings[18][1]
        if tSettings[19] + tSettings[20] == Delay:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeFreestylePattern(self, Pattern):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        freeStyleSettings = tSettings[18] + tSettings[19] + tSettings[20] + "0" + Pattern + tSettings[22] + tSettings[
            23] + tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writePatternCommand = self.commands.changeFreeStyleSettingsValue + freeStyleSettings.decode('hex')
        self.btSer.write(writePatternCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        print tSettings[21][1]
        if tSettings[21][1] == Pattern:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeTrainPattern(self, Pattern):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        trainSettings = tSettings[18] + tSettings[19] + tSettings[20] + "0" + Pattern + tSettings[22] + tSettings[
            23] + tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writePatternCommand = self.commands.changeTrainSettingsValue + trainSettings.decode('hex')
        self.btSer.write(writePatternCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        print tSettings[21][1]
        if tSettings[21][1] == Pattern:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeFreeStyleStrength(self, Strength):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        Strength = int(Strength)
        Strength = hex(Strength)
        print Strength
        if Strength.__len__() == 4:
            Strength = Strength[2] + Strength[3]
        elif Strength.__len__() == 3:
            Strength = "0" + Strength[2]
        else:
            return self.defines.FAIL
        freeStyleSettings = tSettings[18] + tSettings[19] + tSettings[20] + tSettings[21] + Strength + tSettings[
            23] + tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writeStrengthCommand = self.commands.changeFreeStyleSettingsValue + freeStyleSettings.decode('hex')
        self.btSer.write(writeStrengthCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        print tSettings[22][1]
        if tSettings[22] == Strength:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeTrainStrength(self, Strength):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        Strength = int(Strength)
        Strength = hex(Strength)
        print Strength
        if Strength.__len__() == 4:
            Strength = Strength[2] + Strength[3]
        elif Strength.__len__() == 3:
            Strength = "0" + Strength[2]
        else:
            return self.defines.FAIL
        trainSettings = tSettings[18] + tSettings[19] + tSettings[20] + tSettings[21] + Strength + tSettings[
            23] + tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writeStrengthCommand = self.commands.changeTrainSettingsValue + trainSettings.decode('hex')
        self.btSer.write(writeStrengthCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        print tSettings[22][1]
        if tSettings[22] == Strength:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeFreeStylePeriods(self, Periods):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        Periods = int(Periods)
        Periods = hex(Periods)
        print Periods
        if Periods.__len__() == 4:
            Periods = Periods[2] + Periods[3]
        elif Periods.__len__() == 3:
            Periods = "0" + Periods[2]
        else:
            return self.defines.FAIL
        freeStyleSettings = tSettings[18] + tSettings[19] + tSettings[20] + tSettings[21] + tSettings[22] + Periods + tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writePatternPeriods = self.commands.changeFreeStyleSettingsValue + freeStyleSettings.decode('hex')
        self.btSer.write(writePatternPeriods)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        if tSettings[23] == Periods:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeTrainPeriods(self, Periods):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        Periods = int(Periods)
        Periods = hex(Periods)
        print Periods
        if Periods.__len__() == 4:
            Periods = Periods[2] + Periods[3]
        elif Periods.__len__() == 3:
            Periods = "0" + Periods[2]
        else:
            return self.defines.FAIL
        trainSettings = tSettings[18] + tSettings[19] + tSettings[20] + tSettings[21] + tSettings[22] + Periods + tSettings[24] + tSettings[25]
        # print self.commands.changeFreeStyleRangeValue
        writePatternPeriods = self.commands.changeTrainSettingsValue + trainSettings.decode('hex')
        self.btSer.write(writePatternPeriods)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        if tSettings[23] == Periods:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeFreeStyleStopSec(self, StopSec):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        StopSec = int(StopSec)
        StopSec = hex(StopSec * 10)
        print StopSec
        if StopSec.__len__() == 5:
            StopSec = StopSec[3] + StopSec[4] + "0" + StopSec[2]
        elif StopSec.__len__() == 6:
            StopSec = StopSec[4] + StopSec[5] + StopSec[3] + StopSec[2]
        else:
            StopSec = StopSec[2] + StopSec[3] + "0" + "0"
        freeStyleSettings = tSettings[18] + tSettings[19] + tSettings[20] + tSettings[21] + tSettings[22] + tSettings[23] + StopSec
        # print self.commands.changeFreeStyleRangeValue
        writeStopsecCommand = self.commands.changeFreeStyleSettingsValue + freeStyleSettings.decode('hex')
        self.btSer.write(writeStopsecCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readFreestyleSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        if tSettings[24] + tSettings[25] == StopSec:
            return self.defines.PASS
        return self.defines.FAIL

    def ChangeTrainStopSec(self, StopSec):
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        time.sleep(0.5)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        StopSec = int(StopSec)
        StopSec = hex(StopSec * 10)
        print StopSec
        if StopSec.__len__() == 5:
            StopSec = StopSec[3] + StopSec[4] + "0" + StopSec[2]
        elif StopSec.__len__() == 6:
            StopSec = StopSec[4] + StopSec[5] + StopSec[3] + StopSec[2]
        else:
            StopSec = StopSec[2] + StopSec[3] + "0" + "0"
        trainSettings = tSettings[18] + tSettings[19] + tSettings[20] + tSettings[21] + tSettings[22] + tSettings[
            23] + StopSec
        # print self.commands.changeFreeStyleRangeValue
        writeStopsecCommand = self.commands.changeTrainSettingsValue + trainSettings.decode('hex')
        self.btSer.write(writeStopsecCommand)
        time.sleep(1)
        self.FlushInput()
        self.FlushOutput()
        self.btSer.write(self.commands.readTrainSettingsValue)
        hexIn = self.btSer.read(26).encode('hex')
        if hexIn.__len__() < 26:
            return self.defines.FAIL
        tSettings = [hexIn[i:i + 2] for i in range(0, len(hexIn), 2)]
        print tSettings
        if tSettings[24] + tSettings[25] == StopSec:
            return self.defines.PASS
        return self.defines.FAIL

