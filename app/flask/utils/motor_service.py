'''
Sets motors pwm signals to min values
'''
from motors import BLDC

motors = BLDC.from_csv()
motors[0].min_value = 825
motors[3].min_value = 825
[m.set_speed(0) for m in motors]
