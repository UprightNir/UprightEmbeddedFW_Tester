import serial
import Defines
import time
import Btool

class Arduino:
    arduinoComPort = 'COM5'
    defines = Defines.Defines()
    #  arduino com port init
    arduinoSer = serial.Serial(arduinoComPort, 9600, timeout=defines.timeout_time)

    def OpenPort(self):
        self.arduinoSer.open()

    def ClosePort(self):
        self.arduinoSer.close()

    def FlushInput(self):
        self.arduinoSer.flushInput()

    def FlushOutput(self):
        self.arduinoSer.flushOutput()

    def reset_arduino_serial(self):
         self.arduinoSer.close()
         self.arduinoSer.open()
         time.sleep(self.defines.Arduino_serial_reset_time)

    def setUpright(self, angle, button, calib, led):
        #self.reset_arduino_serial()
        self.arduinoSer.write(','.join(map(str, [angle, button, calib, led])))
        print "(current angle:", (angle), ")"
        if button != 0 and button != 1:
            time.sleep(self.defines.set_angle_time)

    #Verify Short vibration after Turn On vibration
    def VerifyVibShortOn(self):
        start_time = time.time()
        i = 0
        print "waiting for Power On\Off vibration ..."
        # arduino reads vibration pulse and waits forever
        x = self.arduinoSer.read(20)
        if x.__len__() < 20:
            return self.defines.FAIL
        print x
        if x.__contains__('1'):
            return self.defines.PASS
        return self.defines.FAIL

    def VerifyVibShortOff(self):
        i = 0
        print "waiting for Power On\Off vibration ..."
        # arduino reads vibration pulse and waits forever
        x = self.arduinoSer.read(20)
        if x.__len__() < 20:
            print "Too short"
            print x
            return self.defines.FAIL
        print x
        if x.__contains__('1'):
            return self.defines.PASS
        return self.defines.FAIL

    # Power On command with arduino
    def ShortPushButton(self):
        self.FlushOutput()
        self.FlushInput()
        self.setUpright(self.defines.NO_ANGLE , 1, 0, 0)
        time.sleep(1)
        #return self.VerifyVibShortOn()

    # Power Off command with arduino
    def LongPushButton(self):
        time.sleep(1)
        self.FlushOutput()
        self.FlushInput()
        self.setUpright(self.defines.NO_ANGLE , 0, 0, 0)
        time.sleep(2)
        #return self.VerifyVibShortOn()

    #Wait for calibration vibration
    def waitForCalibrationVib(self):
        i = 0
        counter = 0
        print "waiting for Power calibration vibration ..."
        x = self.arduinoSer.read(15)
        if x.__len__() < 15:
            return self.defines.FAIL
        print x
        if x.__contains__('1'):
            return True
        return False

    #  return true when vibration occurred
    def waitForVib(self, timeout, deltaAngle, sensitivityAngle):
        start_time = time.time()
        print "waiting for vibration..."
        #  arduinoSer.setTimeout = timout
        x = 0  # reset previous value
        while 1:
            print "Start vibration interupt loop"
            #  arduino reads vibration pulse:
            x = self.arduinoSer.read()
            print "Read Data serial = " + str(x)
            if x == '1':
                delta_vibration_time=int(time.time()-start_time)
                print "Vibration active, Delta T: " + str(delta_vibration_time)
                # logfile.write(" Vibration active, Delta T = " +str(delta_vibration_time)+"\n")
                #logfile.write("Vibration active \t")  # write data to file
                if deltaAngle > sensitivityAngle:
                    #logfile.write("pass \n")
                    return True
                else:
                    #logfile.write("Fail! \n")
                    return False
            else:
                print " no vibration occurred"
                #logfile.write("no vibration occurred \t")
                if deltaAngle > sensitivityAngle:
                    #logfile.write("Fail! \n")
                    return False
                else:
                    #logfile.write("Pass \n")
                    return True

    def DoublePushButton(self, angle):
        time.sleep(1)
        self.FlushOutput()
        self.FlushInput()
        self.setUpright(angle, 2, 0, 0)


    def VerifyManualCalibration(self, btool, isConnected):
        if self.waitForCalibrationVib():
            time.sleep(3)
            if isConnected:
                return btool.CheckCalibration()
            else:
                return self.defines.PASS
        else:
            return self.defines.FAIL
        # print "TO DO sensitivity"
        #time.sleep(3)  # there is a need to delay until upright finish calibration

    def ManualCalibNoWait(self, angle):
        self.setUpright(angle, 2, 0, 0)
        time.sleep(3)

    def MoveToSpecificAngle(self, angle):
        self.FlushOutput()
        self.FlushInput()
        time.sleep(1)
        self.setUpright(angle, self.defines.NO_PUSH_BUTTON , 0, 0)
        time.sleep(1)

    def MoveToTrainManual(self):
        self.setUpright(self.defines.NO_ANGLE, 1, 0, 0)

    def MoveToTrackManual(self):
        self.setUpright(self.defines.NO_ANGLE, 1, 0, 0)