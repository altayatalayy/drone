
from data import linear

l = linear(baudrate=115200)

import time
time.sleep(0.5)

l.connect()
#l.loop2()
n = 0
t0 = time.time()
while (n < 200) and (time.time() - t0 < 20):
    m = l.get_data()
    if m:
        print(m)
        n += 1

l.close()
