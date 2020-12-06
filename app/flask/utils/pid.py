from collections import deque

class PID:

    def __init__(self, ref, *k):
        self.ref = ref
        self.KP, self.KD, self.KI = k
        self.queue = deque(maxlen=10)
        self.queue.append((0, 0))

    def __call__(self, val, dt):
        return self.calc(val, dt)

    def calc(self, val, dt):
        error = self.ref - val
        self.queue.append((error, dt))
        rv = 0
        rv += self.KP * error
        rv += self.KD * (error - self.queue[-2][0] / dt)
        rv += self.KI * sum([e * _dt for e, _dt in self.queue])
        #print(f'rv: {rv}')
        return rv

    def set_ref(ref):
        self.ref = ref


class DronePID:
    KP, KD, KI = 0.05, 0.01, 0.01

    def __init__(self, n_motors=4):
        self.pids = [PID(0, self.KP, self.KD, self.KI) for _ in range(n_motors)]

    def __call__(self, dt, val:list):
        return self.mma([pid(v, dt) for pid, v in zip(self.pids, val)])

    def mma(self, val):
        ''' motor mixing algortihm, for x configuration.'''
        t, y, p, r = tuple(val)
        rv = []
        rv.append(t + y + p + r)#front right
        rv.append(t - y + p - r)#front left
        rv.append(t - y - p + r)#back right
        rv.append(t + y - p - r)#back left
        return rv

import time
class Drone:

    def __init__(self, sensor, motors):
        self.controller = DronePID()
        self.motors = motors
        self.sensor = sensor
        time.sleep(1)

        import redis
        self.r = redis.Redis('localhost')
        self.r.delete('_drone_cmd')
        self.start()

        import atexit
        atexit.register(self.quit)

    def run(self):
        t0 = time.time()
        while self._running:
            data = self.sensor.get_data()[-4:]#roll, pitch, yaw, dist
            #print(f'data: {[round(d, 4) for d in data]}')
            if not data:
                time.sleep(0.1)
                continue
            data = data[::-1]
            t1 = time.time()
            cmds, t0 = self.controller(t1 - t0, data), t1
            #print(f'cmds: {cmds}\n')
            time.sleep(0.9)
            import math
            if not math.nan in cmds:
                [m.set_speed(min(max(cmd, 1), 99)) for m, cmd in zip(self.motors, cmds)]

    def command_loop(self):
        def to_str(arr : list):
            rv = f''
            for i, s in enumerate(arr):
                if i == len(arr) - 1:
                    rv += f'{s}'
                else:
                    rv += f'{s},'
            return rv


        cmds = ('get_motor_speeds', 'get_data', 'QUIT', 'START', 'SOFTSTOP', 'STOP')
        while True:
            if self.r.llen('_drone_cmd') == 0:
                time.sleep(0.05)
                continue

            cmd = self.r.lpop('_drone_cmd').decode('utf-8')
            if cmd not in cmds:
                continue

            if cmd == 'START':
                #import multiprocessing
                #self.daemon = multiprocessing.Process(target=self.run)
                #self.daemon.start()
                self._running = True
                import threading
                self.daemon = threading.Thread(target=self.run)
                self.daemon.start()

            elif cmd == 'STOP':
                if not self._running:
                    continue
                self._running = False
                if self.daemon.is_alive():
                    self.daemon.join()

            elif cmd == 'QUIT':
                self.r.delete('_drone_cmd')
                self._running = False
                if self.daemon.is_alive():
                    self.daemon.join()
                break

            elif cmd == 'get_motor_speeds':
                speeds = [m.get_speed() for m in self.motors]
                self.r.rpush('_motor_speeds', to_str(speeds))

            elif cmd == 'get_data':
                print(1)
                data = self.sensor.get_data()
                self.r.rpush('_data_queue', to_str(data))


    def start(self):
        self.r.rpush('_drone_cmd', 'START')

    def stop(self):
        self.r.rpush('_drone_cmd', 'STOP')

    def quit(self):
        print(1)
        self.r.rpush('_drone_cmd', 'QUIT')



