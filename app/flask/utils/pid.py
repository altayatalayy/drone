from collections import deque

class PID:

    def __init__(self, ref, *k):
        self.ref = ref
        self.KP, self.KD, self.KI = k
        self.queue = deque(maxlen=10)
        self.queue.append((0, 0))
        self.prev_e = 0
        self.I = 0
        self.val = 0
        self.error = 0
        self.rv = 0

    def __call__(self, val, dt):
        return self.calc(val, dt)

    def calc(self, val, dt):
        #print(val)
        self.val = val
        error = self.ref - val
        self.error = error
        self.queue.append((error, dt))
        rv = 0
        rv_p = self.KP * error
        rv_d = self.KD * ((error - self.prev_e) / dt)
        self.prev_e = error
        self.I += self.KI * error * dt
        rv_i = self.I#sum([e * _dt for e, _dt in self.queue])
        rv = rv_p + rv_d + rv_i
        #for plotting only
        self.rv_p = rv_p
        self.rv_d = rv_d
        self.rv_i = rv_i
        self.rv = rv
        #print(f'rv: {rv}')
        return rv

    def set_ref(self, ref):
        self.ref = ref

class DronePID:
    KP, KD, KI = 0.05, 0.01, 0.01

    def get_throttle(self, *args):
        return self.throttle

    def set_throttle(self, throttle):
        self.throttle = throttle

    def __init__(self, n_motors=4):
        self.pids = []
        dist = PID(20, 2, 0, 0)
        roll = PID(0, 0.12/4.6, 0.05*0.1, 0.000)
        pitch = PID(0, 0.12/4.8, 0.05*0.1, 0.000)
        yaw = PID(0, 0, 0, 0)
        self.throttle = 0
        dist.calc = self.get_throttle
        self.pids = [dist, yaw, pitch, roll]
        self.gain = 1

    def __call__(self, dt, val:list):
        #print(val)
        val = [self.gain * pid(v, dt) for pid, v in zip(self.pids, val)]
        #[print(f'pid{i} output: {v}') for i, v in enumerate(val)]
        return self.mma(val)

    def mma(self, val):
        ''' motor mixing algortihm, for x configuration.'''
        t, y, p, r = tuple(val)
        rv = []
        rv.append(t + y + p + r)#front right
        rv.append(t - y + p - r)#front left
        rv.append(t - y - p + r)#back right
        rv.append(t + y - p - r)#back left
        return rv

    def increase_gain(self, val):
        self.gain = self.gain * val

    def get_pid_data(self, idx):
        p = self.pids[idx]
        return [p.ref, p.val, p.error, p.rv]

