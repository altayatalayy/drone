from data import linear
import time

l = linear(baudrate=115200)
l.connect()


def get_data():
    data = list(l.get_data())
    acc, gyr, mag = data[:3], data[3:6], data[6:9]
    return acc, gyr, mag

'''
time.sleep(5)

print(l.get_data())
print(l.get_data())
time.sleep(5)
print(l.get_data())
time.sleep(3)
print(l.get_data())
'''

def to_rad(q):
    from scipy.spatial.transform import Rotation
    q1 = np.append(q[1:], q[0])#from w,x,y,z -> x,y,z,w
    return Rotation.from_quat(q1).as_euler('xyz', degrees=True)


import numpy as np
from ahrs.filters import Madgwick
import ahrs

madgwick = Madgwick()
q = np.array([1,0,0,0], dtype = float)#qw,qx,qy,qz

'''
time.sleep(0.1)
acc1, gyr1, mag1 = get_data()
q = madgwick.updateMARG(Q0, gyr1, acc1, mag1)
'''
t0 = time.time()

while True:
    acc, gyr, mag = get_data()
    q = madgwick.updateMARG(q, gyr=gyr, acc=acc, mag=mag)
    time.sleep(0.05)
    t1 = time.time()
    if t1 - t0 > 1/2:
        print(f'q:{q}\nto_rad:{ahrs.Quaternion(q).to_angles()}')
        t0 = t1

#ahrs.utils.plot_quaternions(Q)
