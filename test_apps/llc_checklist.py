#!/usr/bin/env python

try:
    import acq400_hapi
except Exception:
    print "Please run the following command to instantiate acq400_hapi and then reboot:"
    print "cp /mnt/packages.opt/38-custom_hapi* /mnt/packages/"
    exit(1)
import subprocess


def hex_reg_to_bin(reg):
    """
    Takes the hex representation of a web page register and returns the
    binary representation of it.
    """
    bin_reg = bin(int(reg, 16))[2:].zfill(32)
    return bin_reg


def print_status_register_field(reg, stat):
    """
    Takes a full 32 bit binary register and returns the descriptor address,
    descriptor interrupt enable, descriptor length, and descriptor ID.
    """
    original_reg = reg
    reg = reg[::-1]
    print "Descriptor_address: {:>41}".format(reg[10:32][::-1])
    # print "Descriptor_interrupt_enable: {:>11}".format(reg[8][::-1])
    print "Descriptor_length: {:>24}".format(reg[4:8][::-1])
    if stat:
        print "Size transferred (bytes): {:>16} - Calculated like so:" \
        " (DSCRPT_LEN + 1) * 64 bytes.".format((int(reg[4:8][::-1], 2) + 1)*64)
    else:
        print "Size transferred (Kbytes): {:>16} - Calculated like so:" \
        " 2^(DSCRPT_LEN) * 1Kbyte.".format(2**(int(reg[4:8][::-1], 2)))

    print "Descriptor_id: {:>28}".format(reg[0:4][::-1])
    return None


def print_ctrl_register_fields(reg):
    """
    Takes the full 32 bit binary DMA_CTRL register and prints the
    relevant fields.
    """
    original_reg = reg
    reg = reg[::-1]
    print "PULL_DESCRIPTOR_MODE: {:>18} - pull descriptors are operating in " \
    "{} based mode.".format(reg[31], "RAM" if int(reg[31]) else "FIFO")

    if int(reg[31]): # If operating in RAM descriptor mode then print the length
        with open('/sys/kernel/debug/mgt400/mgt400.A/DMA_PULL_DESC_LEN.0x2024') as PDLR:
            PULL_DMA_DESCRIPTOR_LENGTH_REG = PDLR.read()[0:-1]
            print "PULL_DMA_DESCRIPTOR_LENGTH_REG: {:>17} (Number of " \
            "descriptors, printed because in RAM mode)".format(PULL_DMA_DESCRIPTOR_LENGTH_REG)

    print "RECYCLE_PULL_DESCRIPTOR: {:>15} - pull descriptors are {}being " \
    "recycled.".format(reg[22], "" if int(reg[22]) else "not ")

    print "PULL_LOW_LATENCY: {:>22} - pull descriptors are configured " \
    "for {}.".format(reg[21], "Low Latency" if int(reg[21]) else "streaming")

    print "PULL_FIFOS_RESET: {:>22} - pull FIFOs " \
    "are {}being reset.".format(reg[20], "" if int(reg[20]) else "not ")

    print "PULL_ENABLE: {:>27} - pull descriptors " \
    "are {}enabled.".format(reg[16], "" if int(reg[16]) else "not ")

    print ""

    print "PUSH_DESCRIPTOR_MODE: {:>18} - push descriptors are operating in " \
    "{} based mode.".format(reg[15], "RAM" if int(reg[15]) else "FIFO")

    if int(reg[15]): # If operating in RAM descriptor mode then print the length
        with open('/sys/kernel/debug/mgt400/mgt400.A/DMA_PUSH_DESC_LEN.0x2020') as PDLR:
            PUSH_DMA_DESCRIPTOR_LENGTH_REG = PDLR.read()[0:-1]
            print "PUSH_DMA_DESCRIPTOR_LENGTH_REG: {:>17} (Number of " \
            "descriptors, printed because in RAM mode)".format(PUSH_DMA_DESCRIPTOR_LENGTH_REG)

    print "RECYCLE_PUSH_DESCRIPTOR: {:>15} - push descriptors " \
    "are {}being recycled.".format(reg[6], "" if int(reg[6]) else "not ")

    print "PUSH_LOW_LATENCY: {:>22} - push descriptors are configured " \
    "for {}.".format(reg[5], "Low Latency" if int(reg[5]) else "streaming")

    print "PUSH_FIFOS_RESET: {:>22} - push FIFOs are " \
    "{}being reset.".format(reg[4], "" if int(reg[4]) else "not ")

    print "PUSH_ENABLE: {:>27} - push descriptors are " \
    "{}enabled.".format(reg[0], "" if int(reg[0]) else "not ")

    return [int(reg[21]), int(reg[5])]


def check_clocks(uut):
    print "Clock is set to: {:>30}".format(uut.s1.clk)
    print "Site 1 has CLKDIV: {}".format(uut.s1.clkdiv)
    print "Clock mux set to: {:>5}".format(uut.s0.SYS_CLK_FPMUX.split(" ")[1])
    print "d1 clock: {} Hz".format(uut.s0.SIG_CLK_MB_FREQ.split(" ")[1])
    print "d2 clock: {} Hz".format(uut.s0.SIG_CLK_S1_FREQ)
    return None


def check_aggregator(uut):
    agg0 = uut.s0.aggregator
    aggA = uut.cA.aggregator
    aggB = uut.cB.aggregator

    print "\nSite 0 aggregator configured to:  {}".format(agg0)
    print "Site 12 aggregator configured to: {}".format(aggA)
    print "Site 13 aggregator configured to: {}".format(aggB)
    if agg0.split(" ")[1] == "sites=none":
        print "Aggregator is not configured."
    if agg0.split(" ")[1] != aggA.split(" ")[1] \
    or agg0.split(" ")[1] != aggB.split(" ")[1]:
        print "Aggregator settings are not identical."
    print ""
    return None


def check_distributor(uut):
    dist0 = uut.s0.distributor
    TCAN = dist0.split(" ")[3].split("=")[1]
    print "TCAN configured as: {}".format("Off" if TCAN == "0" else TCAN)
    print ""
    print "Site 0 distributor configured to: {}".format(dist0)
    if dist0.split(" ")[1] == "sites=none":
        print "Distributor is not configured."

    return None


def check_spad(uut):
    spad0 = uut.s0.spad
    spadA = uut.cA.spad
    spadB = uut.cB.spad
    print "Site  0 SPAD configured as: {} {}".format(spad0, "(Off)" if spad0 == "0,0,0" else "")
    print "Site 12 SPAD configured as: {}".format("Off" if spadA == "0" else spadA)
    print "Site 13 SPAD configured as: {}".format("Off" if spadB == "0" else spadB)
    print ""
    return None


# def check_cables_vs_distributor(cables, distributor):
#


def check_mb_sites(uut):
    print ""
    command1 = "show_mb"
    command2 = "list-sites"
    process = subprocess.Popen(command1, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print output
    process = subprocess.Popen(command2, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print output
    return None

def check_sfp(uut):
    MOD_VER = {
    '00': '2.5G Aurora Interface. Compatible with Single Port Single Lane Gen1 ' \
    'PCIe ACQ-FIBER-HBA board ',

    '01': '6.0G Aurora Interface. Compatible with 4 Port Port 4 Lane Gen2 PCIe' \
    ' AFHBA404 board - this version should be deprecated once the AFHBAs have been standardised ',

    '10': '2.5G Aurora Interface with message (LLP) level error detection / ' \
    'retry. Compatible with KMCU and KMCUZ30 boards not with ACQ-FIBER-HBA ',

    '11': '6.0G Aurora Interface with message (LLP) level error detection / ' \
    'retry. Compatible with 4 Port Port 4 Lane Gen2 PCIe AFHBA404 board '
    }

    print ""
    with open('/sys/kernel/debug/mgt400/mgt400.A/MOD_ID.0x00') as MODID:
        MOD_ID = MODID.read()[0:-1]
        MOD_VERSION = MOD_ID[4:6]
        print "MGT482 Module ID: {} {}".format(MOD_ID, MOD_VER[MOD_VERSION])
    sfp_port_status = []
    ports = ["A","B","C","D"]
    try:
        for index, cable in enumerate([1,2,3,4]):
            with open('/dev/gpio/MGT482/SFP{}/PRESENT'.format(cable), 'r') as file:
                status = "Present" if int(file.read()) else "Not Present"
                print "SFP Module {}: {}".format(ports[index], status)
                sfp_port_status.append(status)
    except IOError as e:
        print "Error checking for SFP. Are you sure the MGT-SFP is fitted?"

    # check_cables_vs_distributor(sfp_port_status, uut.s0.distributor)

    print ""
    print "Comms A Aurora Enable: {:>3}".format(uut.cA.aurora_enable)
    print "Comms A Aurora Errors: {:>3}".format(uut.cA.aurora_errors)
    print "Comms A Aurora Lane Up: {:>2}".format(uut.cA.aurora_lane_up)
    print "Comms A Aurora auto DMA: {}".format(uut.cA.auto_dma)
    print ""
    print "Comms B Aurora Enable: {:>3}".format(uut.cB.aurora_enable)
    print "Comms B Aurora Errors: {:>3}".format(uut.cB.aurora_errors)
    print "Comms B Aurora Lane Up: {:>2}".format(uut.cB.aurora_lane_up)
    print "Comms B Aurora auto DMA: {}".format(uut.cB.auto_dma)
    print ""

    print "MGT SFP A"
    print "==================================================================="
    with open('/sys/kernel/debug/mgt400/mgt400.A/DMA_CTRL.0x2004') as dma_ctrl:
        DMA_CTRL = dma_ctrl.read()
        DMA_CTRL= DMA_CTRL[0:-1] # remove the extra return character
        DMA_CTRL_BIN = hex_reg_to_bin(DMA_CTRL)
        print "DMA_CTRL Register: {:>30}".format(DMA_CTRL)
        print "Binary representation of DMA_CTRL_REG: {}".format(DMA_CTRL_BIN)
        stats = print_ctrl_register_fields(DMA_CTRL_BIN)
        print ""

    with open('/sys/kernel/debug/mgt400/mgt400.A/DMA_PULL_DESC_SR.0x2014') as dma_pull:
        DMA_PULL = dma_pull.read()
        DMA_PULL = DMA_PULL[0:-1] # remove the extra return character
        DMA_PULL_BIN = hex_reg_to_bin(DMA_PULL)
        print "DMA_PULL_DESC_SR Register: {:>22}".format(DMA_PULL)
        print "Binary representation of DMA_PULL_REG: {:>12}".format(DMA_PULL_BIN)
        print_status_register_field(DMA_PULL_BIN, stats[0])
        print ""

    with open('/sys/kernel/debug/mgt400/mgt400.A/DMA_PUSH_DESC_SR.0x2010') as dma_push:
        DMA_PUSH = dma_push.read()
        DMA_PUSH= DMA_PUSH[0:-1] # remove the extra return character
        DMA_PUSH_BIN = hex_reg_to_bin(DMA_PUSH)
        print "DMA_PUSH_DESC_SR Register: {:>22}".format(DMA_PUSH)
        print "Binary representation of DMA_PUSH_REG: {:>12}".format(DMA_PUSH_BIN)
        print_status_register_field(DMA_PUSH_BIN, stats[1])
        print ""

    print "MGT SFP B"
    print "==================================================================="
    with open('/sys/kernel/debug/mgt400/mgt400.B/DMA_CTRL.0x2004') as dma_ctrl:
        DMA_CTRL = dma_ctrl.read()
        DMA_CTRL= DMA_CTRL[0:-1] # remove the extra return character
        DMA_CTRL_BIN = hex_reg_to_bin(DMA_CTRL)
        print "DMA_CTRL Register: {:>30}".format(DMA_CTRL)
        print "Binary representation of DMA_CTRL_REG: {}".format(DMA_CTRL_BIN)
        stats = print_ctrl_register_fields(DMA_CTRL_BIN)
        print ""

    with open('/sys/kernel/debug/mgt400/mgt400.B/DMA_PULL_DESC_SR.0x2014') as dma_pull:
        DMA_PULL = dma_pull.read()
        DMA_PULL = DMA_PULL[0:-1] # remove the extra return character
        DMA_PULL_BIN = hex_reg_to_bin(DMA_PULL)
        print "DMA_PULL_DESC_SR Register: {:>22}".format(DMA_PULL)
        print "Binary representation of DMA_PULL_REG: {:>12}".format(DMA_PULL_BIN)
        print_status_register_field(DMA_PULL_BIN, stats[0])
        print ""

    with open('/sys/kernel/debug/mgt400/mgt400.B/DMA_PUSH_DESC_SR.0x2010') as dma_push:
        DMA_PUSH = dma_push.read()
        DMA_PUSH= DMA_PUSH[0:-1] # remove the extra return character
        DMA_PUSH_BIN = hex_reg_to_bin(DMA_PUSH)
        print "DMA_PUSH_DESC_SR Register: {:>22}".format(DMA_PUSH)
        print "Binary representation of DMA_PUSH_REG: {:>12}".format(DMA_PUSH_BIN)
        print_status_register_field(DMA_PUSH_BIN, stats[1])
        print ""
    return None


def run_main():
    uut = acq400_hapi.Acq2106("localhost")

    print "\nStarting test now.\n"
    print "FPGA Rev: {:>54}".format(uut.s0.fpga_version)
    print "Software Rev: {:>38}".format(uut.s0.software_version)
    print "sync_role status: {:>15}".format(uut.s0.sync_role)

    check_mb_sites(uut)
    check_clocks(uut)
    check_aggregator(uut)
    check_spad(uut)
    check_distributor(uut)
    check_sfp(uut)


if __name__ == '__main__':
    run_main()
