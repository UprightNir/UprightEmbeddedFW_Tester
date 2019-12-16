import platform
import logging
import asyncio

from bleak import BleakClient
from bleak import _logger as logger

character_dict = {
    0x2a00: "Device Name",
    0x2a24: "Model Number String",
    0x2a25: "Serial Number String",
    0x2a26: "Firmware Revision String",
    0x2a27: "Hardware Revision String",
    0x2a28: "Software Revision String",
    0x2a29: "Manufacturer Name String",
    # Upright Data Service Characteristics */
    0xBAA1: "Data Amount",
    0xBAA2: "Data Commands",
    0xBAA3: "Packet Number",
    0xBAA4: "Offline Data",
    0xBAA5: "Online Data",
    0xBAA6: "Time Stamp",
    # Upright Settings Service Characteristics */
    0xBAB1: "Train Settings",
    0xBAB2: "Freestyle Settings",
    0xBAB3: "General Settings",
    0xBAB4: "Session Mode",
    0xBAB5: "Vibration State",
    # Upright Session Service Characteristics */
    0xBAC1: "Calib Commands",
    0xBAC2: "Calib Ack And Data",
    0xBAC3: "Posture Status",
    0xBAC4: "Aligned Angle",
    0xBAC5: "Attached State",
    # Upright Power Service Characteristics */
    0xBAD1: "Battery Level",
    0xBAD2: "Charging State",
    0xBAD3: "Error Code",
    0xBAD4: "Hal Control",
    # Upright Test Service Characteristics */
    0xBAE1: "Sensor Val",
    0xBAE2: "Battery Voltage",
    0xBAE3: "Led Vibration Battery",
    0xBAE4: "Memory Test",
    0xBAE5: "Cycle Test",
    0xBAE6: "Buzzer Command",
    0xBAE7: "Hw Version Command",
    0xBAE8: "Sensor Offset Command",
    # Upright BootLoader Service Characteristics */
    0xBAF2: "Charger State"
}

uuid16_dict = {v: k for k, v in character_dict.items() }

DEVICE_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Device Name"))
# device information
MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Manufacturer Name String")
)
MODEL_NUMBER_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Model Number String")
)
SERIAL_NUMBER_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Serial Number String")
)
HARDWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Hardware Revision String")
)
FIRMWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Firmware Revision String")
)
SOFTWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
   uuid16_dict.get("Software Revision String")
)
# data amount
DATA_AMOUNT_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Data Amount")
)
DATA_COMMANDS_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Data Commands")
)
OFFLINE_DATA_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Offline Data")
)
ONLINE_DATA_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Online Data")
)
TRAIN_SETTINGS_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Train Settings")
)
FREESTYLE_SETTINGS_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Freestyle Settings")
)
GENERAL_SETTINGS = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("General Settings")
)
SESSION_MODE_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Session Mode")
)
VIBRATION_STATE_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Vibration State")
)
# Session
CALIB_COMMANDS_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Calib Commands")
)
CALIB_ACK_AND_DATA_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Calib Ack And Data")
)
POSTURE_STATUS_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Posture Status")
)
ALIGNED_ANGLE_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Aligned Angle")
)
ATTACHED_STATE_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Attached State")
)
# power
BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Level")
)

ERROR_CODE_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Error Code")
)
HAL_CONTROL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Hal Control")
)
# test
SENSOR_VAL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Sensor Val")
)
BATTERY_VOLTAGE_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Voltage")
)

MEMORY_TEST_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Memory Test")
)
CYCLE_TEST_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Cycle Test")
)
BUZZER_COMMAND_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Buzzer Command")
)
SENSOR_OFFSET_COMMAND_UUID ="0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Sensor Offset Command")
)
KEY_PRESS_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(0xffe1)
# I/O test points on SensorTag.
IO_DATA_CHAR_UUID = "f000aa65-0451-4000-b000-000000000000"
IO_CONFIG_CHAR_UUID = "f000aa66-0451-4000-b000-000000000000"


async def run(address, loop, debug=False):
    if debug:
        import sys

        # loop.set_debug(True)
        # l = logging.getLogger("asyncio")
        # l.setLevel(logging.DEBUG)
        # h = logging.StreamHandler(sys.stdout)
        # h.setLevel(logging.DEBUG)
        # l.addHandler(h)

    async with BleakClient(address, loop=loop) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))

        device_name = await client.read_gatt_char(DEVICE_NAME_UUID)
        print(
            "Device Name: {0}".format(
                ":".join(["{:02x}".format(x) for x in device_name[::-1]])
            )
        )

        manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
        print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

        model_number = await client.read_gatt_char(MODEL_NUMBER_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

        serial_number = await client.read_gatt_char(SERIAL_NUMBER_UUID)
        print(
            "Serial Number: {0}".format(
                ":".join(["{:02x}".format(x) for x in serial_number[::-1]])
            )
        )

        hardware_revision = await client.read_gatt_char(HARDWARE_REV_UUID)
        print("Hardware Revision String: {0}".format("".join(map(chr, hardware_revision))))

        firmware_revision = await client.read_gatt_char(FIRMWARE_REV_UUID)
        print("Firmware Revision String: {0}".format("".join(map(chr, firmware_revision))))

        data_amount = await client.read_gatt_char(DATA_AMOUNT_UUID)
        print("Data Amount: {0}".format("".join(map(chr, data_amount))))

        data_commands = await client.read_gatt_char(DATA_COMMANDS_UUID)
        print("Data Commands: {0}".format("".join(map(chr, data_commands))))

        offline_data = await client.read_gatt_char(OFFLINE_DATA_UUID)
        print("Offline Data: {0}".format("".join(map(chr, offline_data))))

        aligned_angle = await client.read_gatt_char(ALIGNED_ANGLE_UUID)
        print("Aligned Angle: {0:x}".format("".join(map(chr, aligned_angle))))

        battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
        print("Battery Level: {0}%".format(int(battery_level[0])))

        def keypress_handler(sender, data):
            print("{0}: {1}".format(sender, data))

        write_value = bytearray([0xa0])
        value = await client.read_gatt_char(IO_DATA_CHAR_UUID)
        print("I/O Data Pre-Write Value: {0}".format(value))

        await client.write_gatt_char(IO_DATA_CHAR_UUID, write_value)

        value = await client.read_gatt_char(IO_DATA_CHAR_UUID)
        print("I/O Data Post-Write Value: {0}".format(value))
        assert value == write_value

        await client.start_notify(KEY_PRESS_UUID, keypress_handler)
        await asyncio.sleep(5.0, loop=loop)
        await client.stop_notify(KEY_PRESS_UUID)


if __name__ == "__main__":
    import os
    print(platform.system())
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "C4:01:B7:34:9C:08"
        if platform.system() != "Darwin"
        else "243E23AE-4A99-406C-B317-18F1BD7B4CBE"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address,loop))