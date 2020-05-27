#!/usr/bin/python


import matplotlib.pyplot as plt
import numpy as np
import acq400_hapi
import argparse
import MDSplus


def _create_time_base(decims):
    print("Starting tb")
    uut = acq400_hapi.Acq400("acq2106_182")
    dt = dt = 1 / ((round(float(uut.s0.SIG_CLK_MB_FREQ.split(" ")[1]), -4)) * 1e-9)

    tb = [ np.zeros(decims[0].shape[-1]) ] * len(decims)
    ttime = 0
    for num, subdecims in enumerate(decims):
        ttime = 0
        for ix, dec in enumerate(subdecims):
            tb[num][ix] = ttime
            ttime += float(dec) * dt
    print("Finished tb")
    return tb


def get_args():
    parser = argparse.ArgumentParser(description='MR Validation')
    parser.add_argument('--path', default="/home/dt100/PROJECTS/ACQ400/ACQ400DRV/", help="path to data files.")
    parser.add_argument('--shots', default="1,2,3,22", type=str, help="Which shots to load.")
    parser.add_argument('--uut', default="acq2106_182", help="uut")
    args = parser.parse_args()
    return args


def get_data(args):
    shots = [ int(val) for val in args.shots.split(",") ]
    print(shots)
    data = []
    decims = []
    for shot in shots:
        data_path = "{}{}.{}.dat".format(args.path, args.uut, shot)
        data.append(np.fromfile(data_path, dtype=np.int16))
        decims_path = "{}{}.{}.dec".format(args.path, args.uut, shot)
        decims.append(np.fromfile(decims_path, dtype=np.int8))
    return decims, data


def plot_data(decims, tb, data):
    fig, axs = plt.subplots(3)
    fig.suptitle('TOP: Decims, MIDDLE: data against linear time BOTTOM: TOP and MIDDLE combined')
    axs[0].plot(tb[0], decims[0])
    for num, shot in enumerate(data):
        axs[1].plot(tb[num], shot[0:2e5])
    axs[2].plot(tb[-1], decims[-1]* 1000)
    axs[2].plot(tb[-1], shot[0:2e5])
    
    plt.show()
    return None


def hdr_dump(args):
    dt=[('a', np.uintc), ('b', np.ulonglong), ('c', np.float32), ('d', np.intc), ('e', np.intc), ('f', np.float32), ('g', np.float32)]

    shots = [ int(val) for val in args.shots.split(",") ]
    for num, shot in enumerate(shots):
        print("Shot {} HDR dump.".format(num))
        hdr = np.fromfile("{}{}.{}.hdr".format(args.path, args.uut, shot), dtype=dt)
        print(hdr)
    return None


def main():
    args = get_args()
    decims, data = get_data(args)
    tb = _create_time_base(decims)
    plot_data(decims, tb, data)
    #hdr_dump(args)
    return None


if __name__ == '__main__':
    main()

