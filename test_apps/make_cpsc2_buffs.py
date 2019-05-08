#!/usr/bin/env python
# convert MA1 AWG file to MA2
# NSAMPLES x 4CH x 2BYTE raw file to
# NSAMPLES x "16CH" x 2BYTES, in 4 x 1MB chunks


import numpy as np
import argparse

MINBUFS = 4             # AWG minimum number of buffers to operate

TRASH_MARK = -32000
# ENDBUF_MARK = 32700
ENDBUF_MARK = 5


def load_wf(args):
    data = np.fromfile(args.datafile, dtype=eval(args.datatype))
    return data


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def extend_to_n_bytes(args, data):
    word_size = 2 if args.datatype == "np.int16" else 4
    final_data = []
    for index, buf in enumerate(data):
        data_size = len(buf) * word_size # Data size in bytes
        pad_samples = (args.size - data_size) / word_size
        print("Pad samples = ", pad_samples)
        chunk = np.append(buf, pad_samples * [ENDBUF_MARK]) # data is 1MB
        final_data.append(chunk)
        print("{} len:{} samples needed: {} data shape {}".
                format(index, len(buf), pad_samples, np.shape(final_data)))
    final_data = np.array(final_data).astype(eval(args.datatype))
    return final_data


def export_data(args, data):
    np.ndarray.tofile(data, args.out)
    return None


def make_buff(args):
    data = load_wf(args)
    data = chunks(data, len(data)/MINBUFS) # split waveform into MINBUFS chunks
    data = extend_to_n_bytes(args, data)
    export_data(args, data)
    return None


def run_main():
    parser = argparse.ArgumentParser(description = 'AWG convert for CPSC2')

    parser.add_argument('--datafile', type=str,
    default="8interleave_sine_int32.dat", help="Which datafile to load.")

    parser.add_argument('--out', type=str, default="4mb_sines.dat",
    help='The name of the output file')

    parser.add_argument('--size', type=int, default=1048576,
    help='Size in bytes of the buffer size required.')

    parser.add_argument('--datatype', type=str, default="np.int32",
    help="16 or 32 bit data size.")

    args = parser.parse_args()

    make_buff(args)


if __name__ == '__main__':
    run_main()
