
from collections import deque
import time
import sys
import redis
import atexit
import time
import numpy as np
import threading
import math

import smbus
from imusensor.MPU9250 import MPU9250
from imusensor.filters import madgwick, kalman

prio_cmd = '_drone_prio_cmd'
cmd = '_drone_cmd'

class Controller:

    def __init__(self, sensor):
        from data import Sensor, Filter
        from pid import DronePID
        from motors import BLDC

        sensorfusion = kalman.Kalman()#madgwick.Madgwick(0.023)
        sensorfusion.roll = 0
        sensorfusion.pitch = 0
        sensorfusion.yaw = 0
        address = 0x68
        bus = smbus.SMBus(1)
        imu = MPU9250.MPU9250(bus, address)
        imu.begin()

        imu.loadCalibDataFromFile("/home/pi/projects/drone/app/flask/utils/calib.json")

        self.pids = DronePID()
        m = BLDC.from_csv()
        self.motors = [m[0], m[3], m[1], m[2]]

        self.sensor = imu#sensor
        self.filter = sensorfusion#Filter()

        self.r = redis.Redis('localhost')
        self.r.delete('_drone_cmd')
        self.r.delete(prio_cmd)

        atexit.register(self.quit)
        t0 = time.time()
        time.sleep(0.5)


        self._running = False
        self.start()

    def set_motor_speeds(self, speeds):
        if type(speeds) not in [list, int, float]:
            return
        if type(speeds) == list:
            [m.set_speed(min(max(speed, 0), 60)) for m, speed in zip(self.motors, speeds)]
        else:
            [m.set_speed(speeds) for m in self.motors]

    def update_filter(self, dt):
        #for _ in range(10):
        self.filter.computeAndUpdateRollPitchYaw(self.sensor.AccelVals[0], self.sensor.AccelVals[1], self.sensor.AccelVals[2], self.sensor.GyroVals[0], \
                self.sensor.GyroVals[1], self.sensor.GyroVals[2], self.sensor.MagVals[0], self.sensor.MagVals[1], self.sensor.MagVals[2], dt)
        return [-self.filter.pitch, self.filter.roll, self.filter.yaw]

    def run(self):
        time.sleep(0.1)
        ts = time.time()
        t0 = ts
        n = 0
        '''
        self.set_motor_speeds(20)
        time.sleep(2)
        '''
        try:
            while self._running:
                ti = time.time()
                data = self.sensor.readSensor()#roll, pitch, yaw, dist
                dt = time.time() - t0
                t0 = time.time()
                rotation = self.update_filter(dt)

                dist = 18
                self.q.append(np.array(rotation))
                self.rotation = sum(self.q)/len(self.q)

                self.dist = dist
                rotation = self.rotation[::-1]

                cmds = self.pids(dt, [dist, *rotation])
                n += 1
                if n%1500 == 0:
                    print(f'freq:{n / (time.time()-ts)}Hz')
                    #print(dt)
                    #print(dt < 1/110)
                if self._run_control:
                    if not math.nan in cmds:
                        if time.time() - ts > 2:
                            self.set_motor_speeds(cmds)

                tf = time.time()
                if(tf-ti < 1/103):
                    time.sleep(1/103 - (tf-ti))

        except Exception as e:
            print(e)
            self.stop()
        finally:
            print('quit')

    def command_loop(self):
        def to_str(arr : list):
            # List of ints to str
            rv = f''
            for i, s in enumerate(arr):
                if i == len(arr) - 1:
                    rv += f'{s}'
                else:
                    rv += f'{s},'
            return rv


        cmds = ('get_motor_speeds', 'get_data', 'QUIT', 'START', 'SOFTSTOP', 'STOP')
        from itertools import count
        ct = count()
        cp = count()
        cy = count()
        cr = count()
        while True:
            while self.r.llen(prio_cmd) > 0:
                cmd = self.r.lpop(prio_cmd).decode('utf-8')
                if cmd not in cmds:
                    continue

                if cmd == 'SOFTSTOP':
                    self.soft_stop()

                elif cmd == 'START':
                    self.start()

                elif cmd == 'STOP':
                    self.stop()

                elif cmd == 'QUIT':
                    self.quit()
                    return



            if self.r.llen('_drone_cmd') == 0:
                time.sleep(0.005)
                continue

            cmd = self.r.lpop('_drone_cmd').decode('utf-8')
            #if cmd not in cmds:
            #    continue

            if cmd == 'get_motor_speeds':
                speeds = [m.get_speed() for m in self.motors]
                self.r.rpush('_motor_speeds', to_str(speeds))

            elif cmd[:8] == 'throttle':
                val = cmd[9:]
                self.pids.set_throttle(float(val))

            elif cmd == 'get_rotation':
                self.r.rpush('_rotation', to_str(self.rotation))

            elif cmd == 'get_bat':
                self.r.rpush('_bat', 0)

            elif cmd == 'get_pid_t_data':
                data = self.pids.get_pid_data(0)
                data.insert(0, next(ct))
                self.r.rpush('_pid_t_data', to_str(data))

            elif cmd == 'get_pid_y_data':
                data = self.pids.get_pid_data(1)
                data.insert(0, next(cy))
                self.r.rpush('_pid_y_data', to_str(data))

            elif cmd == 'get_pid_p_data':
                data = self.pids.get_pid_data(2)
                data.insert(0, next(cp))
                self.r.rpush('_pid_p_data', to_str(data))

            elif cmd == 'get_pid_r_data':
                data = self.pids.get_pid_data(3)
                data.insert(0, next(cr))
                self.r.rpush('_pid_r_data', to_str(data))


    def soft_stop(self):
        print('softstop-begin')
        cur_speeds = [m.get_speed() for m in self.motors]
        cur_speeds = [c*0.75 for c in cur_speeds]
        self.set_motor_speeds(cur_speeds)
        time.sleep(0.6)
        cur_speeds = [m.get_speed() for m in self.motors]
        cur_speeds = [c*0.6 for c in cur_speeds]
        self.set_motor_speeds(cur_speeds)
        time.sleep(0.6)
        self.set_motor_speeds(0)
        print('softstop-end')

    def start(self):
        if not self._running:
            self.rotation = [0,0,0]
            self.q = deque(maxlen=6)
            self.daemon = threading.Thread(target=self.run)
            self.daemon.start()

        self.r.delete(cmd)
        self._running = True
        self._run_control = True
        print('started')
        '''
        self.set_motor_speeds(5)
        time.sleep(0.3)
        self.set_motor_speeds(10)
        time.sleep(0.6)
        self.set_motor_speeds(25)
        time.sleep(1)
        self.set_motor_speeds(30)
        time.sleep(0.8)
        '''

    def stop(self):
        if not self._running:
            return
        self._run_control = False
        print('stopped')
        self.soft_stop()

    def quit(self):
        self.r.delete('_drone_cmd')
        self.stop()
        self._running = False
        try:
            if self.daemon.is_alive():
                self.daemon.join()
        except Exception as e:
            print(e)
        finally:
            self.set_motor_speeds(0)



class ControllerApi:
    '''
    For server to server communication
    '''

    def __init__(self, host='localhost', timeout=3):
        self.r = redis.Redis(host)
        self.timeout = timeout

    def push(self, cmd_typ, msg):
        self.r.rpush(cmd_typ, msg)

    def pop(self, key):
        msg = self.r.lpop(key)
        t0 = time.time()
        while time.time() - t0 < self.timeout:
            if not msg == None:
                return msg
            msg = self.r.lpop(key)
        else:
            raise TimeoutError('no response from server')

    def set_throttle(self, val):
        self.push(cmd, f'throttle:{val:.1f}')

    def get_motor_speeds(self):
        self.push(cmd, 'get_motor_speeds')
        try:
            data = self.pop('_motor_speeds')
        except TimeoutError as e:
            return -1
        else:
            data = data.decode('utf-8').split(',')#csv (e.g. 0,0,0,0)
            data = [int(s) for s in data]
            return data

    def get_rotation(self):
        self.push(cmd, 'get_rotation')
        try:
            data = self.pop('_rotation')
        except TimeoutError as e:
            return -1
        else:
            data = data.decode('utf-8').split(',')#csv (e.g. 0,0,0)
            data = [float(s) for s in data]
            return data

    def get_pid_t_data(self):
        self.push(cmd, 'get_pid_t_data')
        try:
            data = self.pop('_pid_t_data')
        except TimeoutError as e:
            return -1
        else:
            data = data.decode('utf-8').split(',')
            data = [float(d) for d in data]
            return data

    def get_pid_y_data(self):
        self.push(cmd, 'get_pid_y_data')
        try:
            data = self.pop('_pid_y_data')
        except TimeoutError as e:
            return -1
        else:
            data = data.decode('utf-8').split(',')
            data = [float(d) for d in data]
            return data

    def get_pid_p_data(self):
        self.push(cmd, 'get_pid_p_data')
        try:
            data = self.pop('_pid_p_data')
        except TimeoutError as e:
            return -1
        else:
            data = data.decode('utf-8').split(',')
            data = [float(d) for d in data]
            return data

    def get_pid_r_data(self):
        self.push(cmd, 'get_pid_r_data')
        try:
            data = self.pop('_pid_r_data')
        except TimeoutError as e:
            return -1
        else:
            data = data.decode('utf-8').split(',')
            data = [float(d) for d in data]
            return data



    def soft_stop(self):
         self.push(prio_cmd, 'SOFTSTOP')

    def start(self):
        self.push(prio_cmd, 'START')

    def stop(self):
        self.push(prio_cmd, 'STOP')

    def quit(self):
        self.push(prio_cmd, 'QUIT')


