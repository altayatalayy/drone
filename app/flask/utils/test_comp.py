

from data import linear

l = linear(baudrate=115200)
l.connect()

def get_data():
    m = l.get_data()
    acc, gyr = m[:3], m[3:6]
    return acc, gyr

import time
import math

def dist(a, b):
    return math.sqrt((a * a) + (b * b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

time.sleep(5)
gyr_x, gyr_y, gyr_z = 0,0,0
t0 = time.time()
tnow = time.time()
tprev = tnow
c = 0
while time.time() - t0 < 300:
    acc, gyr = get_data()
    tnow = time.time()
    dt = tnow - tprev
    dt = 1/100
    tprev = tnow
    gyr_x += gyr[0] * dt
    gyr_y += gyr[1] * dt
    gyr_z += gyr[2] * dt
    x = get_x_rotation(acc[0], acc[1], acc[2])
    y = get_y_rotation(acc[0], acc[1], acc[2])

    x = 0.98 * math.degrees(gyr_x) + 0.02 * x
    y = 0.98 * math.degrees(gyr_y) + 0.02 * y
    print(x, y, math.degrees(gyr_z))
    c += 1
    print(f'freq: {c/(time.time() - t0)}')



