class Commands:

    #====================================================================BLE commands==========================================
    # B-Tool HEX command:
    init = "\x01\x00\xfe\x26\x08\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
    # hard coded train tester (old tester) mac adress (last 6 bytes resemble, written upside down):
    # C2:5B:51:86:2E:D0
    connect = "\x01\x09\xfe\x09\x00\x00\x01\xD0\x2E\x86\x51\x5B\xC2" # UPRIGHT GO 2
    # B-Tool calibration command:
    # reverse engineering used on Btool to extract the hard coded commands.
    calib = "\x01\x92\xFD\x05\x00\x00\x3B\x00\x00"
    clearCalib = "\x01\x92\xfd\x05\x00\x00\x2B\x00\x03\x00\x00\x00"
    isAttached = "\x01\x8a\xfd\x04\x00\x00\x4c\x00"
    disconnect = "\x01\x0a\xfe\x03\x00\x00\x13"
    GetAngle = "\x01\x8A\xFD\x04\x00\x00\x43\x00"   #UpRight GO 2
    shutDownDevice = "\x01\x92\xFD\x05\x00\x00\x53\x00\x03"
    deepSleepDevice = "\x01\x92\xFD\x05\x00\x00\x53\x00\x08"
    readOnlineData = "\x01\x8A\xFD\x04\x00\x00\x27\x00"
    readcalibAckPoints = "\x01\x8A\xFD\x04\x00\x00\x3D\x00" #command to read calibration ACK and points
    vibrationOff = "\x01\x92\xFD\x05\x00\x00\x37\x00\x01"
    vibrationOn = "\x01\x92\xFD\x05\x00\x00\x37\x00\x00"
    readVibrationStatus = "\x01\x8A\xFD\x04\x00\x00\x37\x00"
    changeFreeStyleSettingsValue = "\x01\x12\xFD\x0E\x00\x00\x00\x00\x30\x00" # different kind of Write request called ATT_REQ
    changeTrainSettingsValue = "\x01\x12\xFD\x0E\x00\x00\x00\x00\x2E\x00" # different kind of Write request called ATT_REQ
    readFreestyleSettingsValue = "\x01\x8A\xFD\x04\x00\x00\x30\x00"
    readTrainSettingsValue = "\x01\x8A\xFD\x04\x00\x00\x2E\x00"