from motors import BLDC
from data import Sensor
from controller import Controller

sensor = Sensor(port='/dev/ttyUSB0', baudrate=115200, n=20)
status = sensor.connect()
print(status)

cont = Controller(sensor)
cont.command_loop()

