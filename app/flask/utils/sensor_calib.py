
import os
import sys
import time
import smbus
import numpy as np

from imusensor.MPU9250 import MPU9250

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()
imu.setAccelRange("AccelRangeSelect2G")
imu.setGyroRange("GyroRangeSelect250DPS")

imu.caliberateGyro()
print(f'calibrated gyro')
imu.caliberateAccelerometer()
print ("Acceleration calib successful")
imu.caliberateMagApprox()
print ("Mag calib successful")

accelscale = imu.Accels
accelBias = imu.AccelBias
gyroBias = imu.GyroBias
mags = imu.Mags
magBias = imu.MagBias

path = '/home/pi/projects/drone/app/flask/utils/calib.json'
imu.saveCalibDataToFile(path)
print ("calib data saved")

imu.loadCalibDataFromFile(path)
if np.array_equal(accelscale, imu.Accels) & np.array_equal(accelBias, imu.AccelBias) & \
    np.array_equal(mags, imu.Mags) & np.array_equal(magBias, imu.MagBias) & \
    np.array_equal(gyroBias, imu.GyroBias):

    print ("calib loaded properly")

