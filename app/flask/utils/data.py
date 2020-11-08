import abc
import threading

class Data(abc.ABC):
    ''' ABC'''

    def __init__(self):
        self.container = []
        self._running = True
        self.daemon = threading.Thread(target=self.loop, daemon=True)
        self._con_lock = threading.Lock()
        self.daemon.start()

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

from itertools import count, chain
c = count()
def f():
    while True:
        i = next(c)
        yield f'x:{i},y:{i},z:{i};x:{i},y:{i},z:{i}'

def parse_ser(s:str):
    '''parse linear data from serial return tuple of float
    ex: x:0,y:0,z:0;x:0,y:0,z:0 -> [0,0,0,0,0,0]
    '''
    acc, gyro = s.split(';')
    return tuple(float(s.split(':')[1]) for s in chain(acc.split(','), gyro.split(',')))

a = f()
class linear(Data):
    ''' stores acc and gyro data'''
    def __init__(self, port='/dev/ttyUSB0', baudrate=19200):
        import serial
        #self.ser = serial.Serial(port, baudrate)
        super().__init__()

    def loop(self):
        #with self.ser as ser:
        while self._running:
            import time
            time.sleep(0.02)
            line = next(a)#ser.readline()# x:0, y:0, z:0; x:0, y:0, z:0
            v = parse_ser(line)
            self.update_con(v)



