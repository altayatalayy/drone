import abc
import threading
import redis
from collections import deque
from itertools import chain
import numpy as np

class Shared:
    '''
        This class modifies the get_data and update_con methods,
        these methods will now use a redis server. This slowsdown the process

        reqirements:
        - Super class must have update_con and get_data methods.
        - a redis server must be running.
    '''
    def __init__(self, *args, **kwargs):
        self.r = redis.Redis('localhost')
        self.key = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def update_con(self, data:'iterable'):
        '''
            We actually dont need to use super().get_data and super().update_con
            in this example, since they dont change the data
            and it seems that they dont decrase execution speed.
        '''

        super().update_con(data)
        data = super().get_data()

        pipe = self.r.pipeline()
        pipe.delete(self.key)
        pipe.lpush(self.key, *data)
        pipe.execute()

    def get_data(self):
        return [float(_) for _ in self.r.lrange(self.key, 0, -1)[::-1]]


class Data(abc.ABC):
    ''' ABC, when initialized starts a daemon thread'''

    def __init__(self, *args, **kwargs):
        self.container = []
        self._running = True
        self.daemon = threading.Thread(target=self.loop, daemon=True)
        self._con_lock = threading.Lock()
        self.daemon.start()
        import atexit
        atexit.register(self.close)
        #super().__init__(*args, **kwargs)

    def get_data(self):
        ''' return copy of data'''
        self._con_lock.acquire()
        rv = list(self.container)
        self._con_lock.release()
        return rv

    def update_con(self, data):
        self._con_lock.acquire()
        if not data:
            self.container = []
        else:
            self.container = data
        self._con_lock.release()


    @abc.abstractmethod
    def loop(self):
        pass

    def close(self):
        self._running = False
        if self.daemon.is_alive():
            self.daemon.join()

###### for testing
from itertools import count
c = count()
def f():
    while True:
        i = next(c)
        yield f'x:{i},y:{i},z:{i};x:{i},y:{i},z:{i+2}'

a = f()
#######


class Averaged:
    '''
        This class modifies update_con. Takes the averages of given data
        to reduce the noise in the data. Equvalent to loww pass filter.?
        idea from: https://www.researchgate.net/post/How_can_I_reduce_noise_from_accelerometer_and_gyroscope_values_of_the_nao_robot_for_classification
    '''

    def __init__(self, *args, n = 10, **kwargs):
        super().__init__(*args, **kwargs)
        self._n = n
        self._q = deque(maxlen=self._n)

    def update(self, data:'iterable'):
        #print(data)
        if len(data) == 6:
            data.append(0)
        self._q.append(np.array(data))
        if not len(self._q) < self._n:
            data = tuple(sum(self._q) / self._n)
            return data



def parse_ser(s:str):
    '''
        parse linear data from serial return tuple of float
        ex: x:0,y:0,z:0;x:0,y:0,z:0;d:0 -> (0,0,0,0,0,0,0)
    '''
    acc, gyro, d, bat = s.split(';')
    #print(acc, gyro, d, bat)
    if bat:
        return tuple(float(str(s)) for s in chain(acc.split(','), gyro.split(','), [d], [bat]))
    return tuple(float(str(s)) for s in chain(acc.split(','), gyro.split(','), [d]))


class Sensor(Averaged):
    def __init__(self, *args, port='/dev/ttyUSB0', baudrate=19200, **kwargs):
        import serial
        #port = '/dev/cu.usbserial-14320'
        self._connected = False
        self.ser = serial.Serial(port, baudrate, timeout=5)
        super().__init__(*args, **kwargs)
        #status = self.connect()
        #if status != -1:
            #self._connected = True

    def readline(self):
        try:
            msg = self.ser.readline().decode('utf-8')[:-2]
        except Exception as e:
            print(e)
        else:
            return msg


    def get_data(self):
        data = self.readline()
        if data:
            try:
                data = parse_ser(data)
            except Exception as e:
                print(f'error:{e}\ndata:{data}')
            else:
                return super().update(data)

    '''
    def loop2(self):
        while True:
            l = self.ser.readline().decode('utf-8')[:-2]
            try:
                l =  parse_ser(l)
            except:
                pass
            else:
                print(l)

    def loop(self):
        #This method will run only on the master process
        while self._running:
            try:
                line = self.ser.readline().decode('utf-8')[:-2]#read bytes from serial, last 2 chars = /r/n
            except Exception as e:
                print(e)
                pass
            else:
                try:
                    v = parse_ser(line)
                except ValueError as e:
                    print(f'error:{e}\nstr:{line}')
                    pass
                except Exception as e:
                    print(f'error:{e}\nline{line}')
                    pass
                else:
                    self.update_con(v)
        return
    '''

    def connect(self):
        import time
        t0 = time.time()
        while time.time() - t0 < 20:
            msg = self.readline()
            if msg == "calibrate mag":
                #input("Press enter")
                self.ser.write('\n'.encode('utf-8'))
                self.ser.flush()
                break
        else:
            return -1

        # calibrate mag
        t0 = time.time()
        while time.time() - t0 < 40:
            msg = self.readline()
            if msg == "OK":
                break
        else:
            return -1
        print('connected')
        self.readline()

    def close(self):
        #this method is registered to run at exit by the data class
        #super().close()
        self.ser.close()

import time
import math
import numpy as np

class Filter:

    def __init__(self, alpha=0.08):
        ''' complementary Filter for gyro and acc '''
        self.gyr = np.array([0, 0, 0], dtype=float)
        self.alpha = alpha

    @staticmethod
    def dist(a, b):
        return math.sqrt(a**2 + b**2)

    def update(self, acc, gyr:np.array, dt):
        ''' returns x,y,z angles in degrees'''

        self.gyr += gyr * dt
        x, y, z = acc
        rot_x = -math.atan2(x, self.dist(y, z))
        rot_y = math.atan2(y, self.dist(x, z))

        x = (1 - self.alpha) * self.gyr[0] + self.alpha * rot_x
        y = (1 - self.alpha) * self.gyr[1] + self.alpha * rot_y
        z = self.gyr[2]
        return x, y, z







