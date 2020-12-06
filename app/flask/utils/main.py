from motors import BLDC
from data import linear

motor_list = BLDC.from_csv()
l = linear(port='/dev/ttyUSB0')

from pid import Drone
drone = Drone(l, motor_list)
drone.command_loop()

