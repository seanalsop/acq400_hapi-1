#!/usr/bin/env python

import sys
import acq400_hapi
from acq400_hapi import intSI as intSI
import argparse
import time
import os
import signal

def disable_trigger(master):
    master.s0.SIG_SRC_TRG_0 = 'DSP0'
    master.s0.SIG_SRC_TRG_1 = 'DSP1'
    
def enable_trigger(master):
    master.s0.SIG_SRC_TRG_0 = 'EXT'
    master.s0.SIG_SRC_TRG_1 = 'STRIG'    
    
def expand_role(urole):
    # fpmaster          # fpclk, fptrg
    # fpmaster,strg     # fpclk, strg
    # master            # mbclk, strg
    # master,fptrg      # mbclk, fptrg
    if urole == "fpmaster,strg":
        return "fpmaster TRG:DX=d1"
    if urole == "master,fptrg":
        return "master TRG:DX=d0"
    return urole

def run_shot(args):
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]
    master = uuts[0]
    if args.enable_trigger:
        enable_trigger(master)
        return
    
    postfix = ""
    if args.clkdiv:
        postfix = "CLKDIV={}".args.clkdiv

    master.s0.sync_role = "{} {} {} {}".format(expand_role(args.toprole), args.fclk, args.fin, postfix)
    disable_trigger(master)
    for slave in uuts[1:]:
        slave.s0.sync_role = "{} {} {} {}".format('slave', args.fclk, args.fin, postfix)
    
def run_main():    
    parser = argparse.ArgumentParser(description='set sync roles for a stack of modules')    
    acq400_hapi.Acq400UI.add_args(parser, post=False)
    parser.add_argument('--enable_trigger', default=None, help="set this to enable the trigger all other args ignored")
    parser.add_argument('--toprole', default='master', help="role of top in stack")
    parser.add_argument('--fclk', default='1000000', help="sample clock rate")
    parser.add_argument('--fin',  default='1000000', help="external clock rate")
    parser.add_argument('--clkdiv', default=None, help="optional clockdiv")
    parser.add_argument('uuts', nargs='+', help="uut ")
    run_shot(parser.parse_args())



# execution starts here

if __name__ == '__main__':
    run_main()
