import time
import matplotlib.pyplot as plt
from data import linear
import numpy as np

for n in range(10, 320, 50):
    data_high_pass = linear(port='/dev/ttyUSB0', n=n) #data with high pass filter
    if n < 50:
        time.sleep(3)
    elif n < 100:
        time.sleep(4)
    elif n < 140:
        time.sleep(6)
    elif n < 200:
        time.sleep(8)
    elif n < 250:
        time.sleep(10)
    else:
        time.sleep(12)

    time.sleep(n/500 + 1.5)
    print('starting...')
    data = np.array([])
    t0 = time.time()
    t1 = t0
    tf = 25
    t = []
    while t1 - t0 < tf:
        if data.shape[0] == 0:
            data = np.array(data_high_pass.get_data())
        else:
            data = np.vstack((data, data_high_pass.get_data()))
        t1 = time.time()
        t.append(round(t1, 6))

    t = np.array(t) - t0
    title = f'complementary 6dof + distance n={n}'
    titles = ['acc_x', 'acc_y', 'acc_z', 'gyr_x', 'gyr_y', 'gyr_z', 'dist']

    means = np.mean(data, axis=0)
    print(f'means: {means}')

    print(f'Elapsed: {t1-t0:7.5f}s update-freq:{data.shape[0]/(t1-t0):5.3f}Hz')
    #t = np.linspace(0, round(t1-t0, 3), len(data))
    fig, axs = plt.subplots(data.shape[1], figsize=(25, 25), sharex=True)
    for i in range(data.shape[1]):
        axs[i].plot(t, data[:, i])
        axs[i].plot([t[0], t[-1]], [means[i], means[i]])
        axs[i].set_title(titles[i])

    fig.suptitle(title, fontsize=24)

    out_file = f'imgs/n_{n}.pdf'
    print(f'saving to {out_file}')
    plt.savefig(out_file)
    data_high_pass.close()
    print(f'finished')
