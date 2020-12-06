import abc
import threading
import redis
from collections import deque
from itertools import chain
import numpy as np

class Averaged:
    '''
        This class modifies update_con. Takes the averages of given data
        to reduce the noise in the data. Equvalent to loww pass filter.?
        idea from: https://www.researchgate.net/post/How_can_I_reduce_noise_from_accelerometer_and_gyroscope_values_of_the_nao_robot_for_classification
    '''

    def __init__(self, *args, n = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self._n = n
        self._q = deque(maxlen=self._n)

    def update_con(self, data:'iterable'):
        self._q.append(np.array(data))
        if not len(self._q) < self._n:
            super().update_con(tuple(sum(self._q) / self._n))

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

def parse_ser(s:str):
    '''
        parse linear data from serial return tuple of float
        ex: x:0,y:0,z:0;x:0,y:0,z:0;d:0 -> (0,0,0,0,0,0,0)
    '''
    acc, gyro, d = s.split(';')
    return tuple(float(s.split(':')[1]) for s in chain(acc.split(','), gyro.split(','), [d]))


class linear(Averaged, Data):
    '''
        Starts a daemon thread that reads from the serial
        stores acc and gyro data as a list on a redis server
        returns the values from the redis server
    '''
    def __init__(self, *args, port='/dev/ttyUSB0', baudrate=19200, **kwargs):
        import serial
        #port = '/dev/cu.usbserial-14320'
        self.ser = serial.Serial(port, baudrate, timeout=5)
        super().__init__(*args, **kwargs)

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

    def close(self):
        #this method is registered to run at exit by the data class
        super().close()
        self.ser.close()
