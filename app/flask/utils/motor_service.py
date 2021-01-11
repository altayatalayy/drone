'''
Sets motors pwm signals to min values
'''
from motors import BLDC

motors = BLDC.from_csv()
[m.set_speed(0) for m in motors]

def set(speed, motors=motors):
    motors[0].set_speed(speed)
    motors[3].set_speed(speed)
    motors[1].set_speed(speed)
    motors[2].set_speed(speed)

