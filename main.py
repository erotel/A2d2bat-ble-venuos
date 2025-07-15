#!/usr/bin/env python3

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import sys
import time
import signal
import struct
import binascii
import logging
from logging.handlers import RotatingFileHandler
from gi.repository import GLib
from threading import Thread

sys.path.append('/opt/velib_python')
from bluepy.btle import Peripheral, DefaultDelegate, BTLEException
from dbusbatteryservice import DbusServiceBattery

BLE_ADDRESS = "A5:C2:37:29:7A:ED"
LOGFILE = "/data/jbd_ble.log"

rotating_handler = RotatingFileHandler(
    LOGFILE, maxBytes=1_000_000, backupCount=3
)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        rotating_handler,
        logging.StreamHandler(sys.stdout)
    ]
)

class JBDDelegate(DefaultDelegate):
    def __init__(self, service):
        DefaultDelegate.__init__(self)
        self.service = service

    def handleNotification(self, cHandle, data):
        hex_data = binascii.hexlify(data).decode('utf-8')
        if 'dd03' in hex_data:
            self.parse_cellinfo1(data)
        elif hex_data.endswith('77') and len(hex_data) in (24, 36):
            self.parse_cellinfo2(data)

    def parse_cellinfo1(self, data):
        i = 4
        volts, amps, remain, capacity, cycles, mdate, balance1, balance2 = struct.unpack_from('>HhHHHHHH', data, i)
        volts = volts / 100
        amps = amps / 100
        remain = remain / 100
        capacity = capacity / 100
        soc = remain / capacity * 100 if capacity > 0 else 0
        # logging.info(f"Voltage: {volts:.2f} V, Current: {amps:.2f} A, SOC: {soc:.1f} %, Capacity: {capacity:.2f} Ah")
        self.service.update_values(volts, amps, soc, capacity)

    def parse_cellinfo2(self, data):
        pass  # optional

def ble_worker(service):
    logging.info(f"Connecting to BLE BMS at {BLE_ADDRESS}")

    max_retries = 5
    retries = 0
    bms = None

    while retries < max_retries:
        try:
            bms = Peripheral(BLE_ADDRESS, addrType="public")
            logging.info("BLE connected.")
            break
        except BTLEException as e:
            retries += 1
            logging.warning(f"BLE connect failed ({retries}/{max_retries}): {e}")
            time.sleep(5)

    if bms is None:
        logging.error(f"Unable to connect to BLE BMS after {max_retries} attempts. Exiting.")
        return

    bms.setDelegate(JBDDelegate(service))

    try:
        while True:
            bms.writeCharacteristic(0x15, b'\xdd\xa5\x03\x00\xff\xfd\x77', False)
            bms.waitForNotifications(5)
            time.sleep(10)
    except BTLEException as e:
        logging.error(f"BLE connection lost during operation: {e}")
    finally:
        logging.info("Disconnecting BLE.")
        try:
            bms.disconnect()
        except Exception:
            pass

def main():
    logging.info("Starting JBD BLE D-Bus bridge")
    service = DbusServiceBattery("com.victronenergy.battery.jbd_ble")
    logging.info("D-Bus service initialized")

    ble_thread = Thread(target=ble_worker, args=(service,))
    ble_thread.daemon = True
    ble_thread.start()

    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *a: exit(0))
    main()
