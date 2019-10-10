#!/usr/bin/python3


"""
This script is intended to test a real data set on all channels of an acq2106
fitted with an MGT-DRAM module. The data should be offloaded first and stored
in the same directory created by mgtdramshot.py.

The script compares zero crossings, so the less zero crossings there are in the
data, the faster the algorithm will be able to validate the data.

NB: This script loads ALL 8GB into RAM.
"""


import numpy as np
import matplotlib.pyplot as plt
import acq400_hapi
import argparse

from os import listdir
from os.path import isfile, join

def main():
    parser = argparse.ArgumentParser(description='acq2106 mgtdram data test.')

    parser.add_argument('uut', nargs=1, help="uut ")
    args = parser.parse_args()

    path = args.uut[0] + "/"
    print("uut = {}".format(args.uut[0]))
    uut = acq400_hapi.Acq400(args.uut[0])

    nchan = uut.nchan()

    files = [f for f in listdir(path) if isfile(join(path, f))]
    files = [int(i) for i in files]
    files.sort()
    files = [str(i) for i in files]

    data_length = int(np.fromfile(path+files[0], dtype=np.int16).shape[-1]/nchan)
    print("data_length = {}".format(data_length))
    data = np.zeros((data_length*2000, nchan), dtype=np.int16)
    print("shape of data = {}".format(data.shape))


    for pos, file in enumerate(files):
        # load file and pick off the correct channels
        print("Loaded {}".format(pos), end='\r')
        raw_data = np.fromfile(path+file, dtype=np.int16)
        place = pos * data_length
        for ii in range(0,nchan):
            data[:,ii][place:place+data_length] = raw_data[ii::16]

    raw_data = None


    for ch in range(0,nchan):
        zero_crossings = np.where(np.diff(np.sign(data[:,ch])))[0]
        # print("Zero crossings shape: {}".format(zero_crossings.shape[-1]))

        # By increasing the amount of data we compare at one time we can
        # greatly increase the speed of analysis
        zero_crossings_reduced = zero_crossings[0::100]
        for pos, val in enumerate(zero_crossings_reduced):
            try:
                this_block = data[:,ch][val:zero_crossings_reduced[pos+1]]
            except Exception:
                print("\n Finished.")
                break
            test_block = data[:,ch][zero_crossings[20]:zero_crossings[20]+this_block.shape[-1]]

            close = np.allclose(this_block, test_block, rtol=300, atol=900)
            # is_close = np.isclose(this_block, test_block, rtol=300, atol=900)

            if pos % 50 == 0:
                pc = round(pos / len(zero_crossings_reduced) * 100, 2)
                print(pc, ' percent complete     ', end='\r')

            if not close:
                print("Failed! Not close. Failed at block: {}, {}".format(val, pos))
                plt.plot(this_block)
                plt.plot(test_block)
                # plt.plot(is_close)
                plt.show()


if __name__ == '__main__':
    main()
