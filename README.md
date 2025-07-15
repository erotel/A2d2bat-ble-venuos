Connecting a2d2 battery to venus os on raspberry via bluetooth

opkg update
opkg install git
opkg install python3-dbus python3-pygobject python3-pip
pip3 install bluepy
cd /opt
git clone https://github.com/victronenergy/velib_python.git
