from motors import BLDC
from data import Sensor
from controller import Controller

#sensor = Sensor(port='/dev/ttyUSB0', baudrate=115200, n=10)
#status = sensor.connect()
#print(status)
sensor = None

cont = Controller(sensor)
cont.command_loop()

