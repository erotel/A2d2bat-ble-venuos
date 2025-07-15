import dbus
from vedbus import VeDbusService

class DbusServiceBattery:
    def __init__(self, servicename):
        self._dbusservice = VeDbusService(servicename, register=False)

        # Basic management paths
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path('/Mgmt/ProcessVersion', '1.0')
        self._dbusservice.add_path('/Mgmt/Connection', 'com.jbd.ble')

        # Device identification
        self._dbusservice.add_path('/DeviceInstance', 512)
        self._dbusservice.add_path('/ProductId', 0xFFFF)
        self._dbusservice.add_path('/ProductName', 'JBD BLE BMS')
        self._dbusservice.add_path('/FirmwareVersion', '0.1')
        self._dbusservice.add_path('/HardwareVersion', '0.1')
        self._dbusservice.add_path('/Connected', 1)

        # Main battery values
        self._dbusservice.add_path('/Dc/0/Voltage', 0.0)
        self._dbusservice.add_path('/Dc/0/Current', 0.0)
        self._dbusservice.add_path('/Dc/0/Power', 0.0)
        self._dbusservice.add_path('/Soc', 0.0)
        self._dbusservice.add_path('/Capacity', 0.0)
        self._dbusservice.add_path('/InstalledCapacity', 100.0)
        self._dbusservice.add_path('/TimeToGo', 0)

        # Battery configuration
        self._dbusservice.add_path('/System/NrOfCells', 4)

        # Finalize registration after all mandatory paths
        self._dbusservice.register()

    def update_values(self, voltage, current, soc, capacity):
        self._dbusservice['/Dc/0/Voltage'] = voltage
        self._dbusservice['/Dc/0/Current'] = current
        self._dbusservice['/Dc/0/Power'] = voltage * current
        self._dbusservice['/Soc'] = soc
        self._dbusservice['/Capacity'] = capacity