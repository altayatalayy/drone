
import time
import sys
import redis
import atexit
import time
import numpy as np

import smbus
from imusensor.MPU9250 import MPU9250
from imusensor.filters import madgwick

prio_cmd = '_drone_prio_cmd'
cmd = '_drone_cmd'

class Controller:

    def __init__(self, sensor):
        from data import Sensor, Filter
        from pid import DronePID
        from motors import BLDC

        sensorfusion = madgwick.Madgwick(0.01)
        address = 0x68
        bus = smbus.SMBus(1)
        imu = MPU9250.MPU9250(bus, address)
        imu.begin()

        imu.loadCalibDataFromFile("/home/pi/projects/drone/app/flask/utils/calib.json")



        self.pids = DronePID()
        self.motors = BLDC.from_csv()
        self.sensor = imu#sensor
        self.filter = sensorfusion#Filter()

        self.r = redis.Redis('localhost')
        self.r.delete('_drone_cmd')
        self.r.delete(prio_cmd)

        atexit.register(self.quit)
        t0 = time.time()
        time.sleep(0.5)

        self.rotation = [0,0,0]
        self.dist = 0

        self.start()

    def set_motor_speeds(self, speeds):
        if type(speeds) not in [list, int, float]:
            return
        if type(speeds) == list:
            [m.set_speed(min(max(speed, 0), 100)) for m, speed in zip(self.motors, speeds)]
        else:
            [m.set_speed(speeds) for m in self.motors]

    def run(self):
        time.sleep(0.1)
        '''
        while not self.filter._is_calibrated:
            data = self.sensor.get_data()
            if not data:
                continue
            acc = data[:3]
            self.filter.calibrate(acc)
        '''

        ts = time.time()
        t0 = ts
        n = 0

        while self._running:
            data = self.sensor.readSensor()#roll, pitch, yaw, dist
            '''
            if not data:
                time.sleep(0.01)
                continue
            '''
            #data = data[::-1]
            for _ in range(10):
                t1 = time.time()
                dt = t1 - t0
                t0 = t1
                self.filter.updateRollPitchYaw(self.sensor.AccelVals[0], self.sensor.AccelVals[1], self.sensor.AccelVals[2], self.sensor.GyroVals[0], \
                        self.sensor.GyroVals[1], self.sensor.GyroVals[2], self.sensor.MagVals[0], self.sensor.MagVals[1], self.sensor.MagVals[2], dt)


            #acc, gyr = data[:3], data[3:6]
            #rotation = self.filter.update(acc, np.array(gyr, dtype=float), dt)
            dist = 18#data[6]
            #print(f'data: {[round(d, 4) for d in data]}')
            #print(round(dt, 5))
            #print(dist)
            self.rotation = [self.filter.pitch, self.filter.roll, self.filter.yaw]
            self.dist = dist
            rotation = self.rotation[::-1]
            cmds = self.pids(dt, [dist, *rotation])
            #print(f'cmds: {cmds}\n')
            #n += 1
            #print(f'freq:{n / (time.time()-ts)}Hz')
            import math
            if not math.nan in cmds:
                #print(f'\n')
                pass
                #self.set_motor_speeds(cmds)
                #[m.set_speed(min(max(cmd, 0), 100)) for m, cmd in zip(self.motors, cmds)]

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
                    self.r.delete('_drone_cmd')
                    self.stop()
                    self.set_motor_speeds(0)
                    return



            if self.r.llen('_drone_cmd') == 0:
                time.sleep(0.05)
                continue

            cmd = self.r.lpop('_drone_cmd').decode('utf-8')
            #if cmd not in cmds:
            #    continue

            if cmd == 'get_motor_speeds':
                speeds = [m.get_speed() for m in self.motors]
                self.r.rpush('_motor_speeds', to_str(speeds))

            elif cmd == 'get_rotation':
                self.r.rpush('_rotation', to_str(self.rotation))

            elif cmd == 'get_bat':
                self.r.rpush('_bat', 0)

            elif cmd == 'get_pid_t_data':
                data = self.pids.get_pid_data(0)
                data.insert(0, next(cr))
                self.r.rpush('_pid_t_data', to_str(data))

            elif cmd == 'get_pid_y_data':
                data = self.pids.get_pid_data(1)
                data.insert(0, next(cr))
                self.r.rpush('_pid_y_data', to_str(data))

            elif cmd == 'get_pid_p_data':
                data = self.pids.get_pid_data(2)
                data.insert(0, next(cr))
                self.r.rpush('_pid_p_data', to_str(data))

            elif cmd == 'get_pid_r_data':
                data = self.pids.get_pid_data(3)
                data.insert(0, next(cr))
                self.r.rpush('_pid_r_data', to_str(data))


    def soft_stop(self):
        cur_speeds = [m.get_speed() for m in self.motors]
        cur_speeds = [c*0.5 for c in cur_speeds]
        self.set_motor_speeds(cur_speeds)
        time.sleep(0.3)
        self.set_motor_speeds(0)

    def start(self):
        self._running = True
        import threading
        self.daemon = threading.Thread(target=self.run)
        self.daemon.start()

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self.daemon.is_alive():
            self.daemon.join()

    def quit(self):
        pass



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


