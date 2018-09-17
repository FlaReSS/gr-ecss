#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#
import numpy as np
import matplotlib.pyplot as plt
import math, sys, os
import matplotlib.pyplot as plt

def sine(freq, samp, size):
    sine = []
    phase = 0
    delta_phase = (2 * math.pi * freq) / samp
    for i in range(size):
        if (abs(phase) > math.pi):
          while (phase > math.pi):
            phase -= 2 * math.pi
          while (phase < -math.pi):
            phase += 2 * math.pi;
        sine.append( math.sin(phase))
        phase += delta_phase
    return sine

def groetzel(signal, freq, samp, size):
    k = (int) (0.5 + ((size * freq) / samp))
    coeff = 2 * math.cos((float)((2 * math.pi / size) * k))
    output = []
    for r in range(len(signal)/size):
        Q1 = 0.0;
        Q2 = 0.0;
        for i in range(size):
            Q0 = signal[(r * size) + i] + (coeff * Q1) - Q2
            Q2 = Q1
            Q1 = Q0
        magnitude_2 = (Q1 * Q1) + (Q2 * Q2) - (Q1 * Q2 * coeff)
        output.append((float)(magnitude_2) / (size * size))
    mean = np.mean(output)
    var = np.var(output)
    return mean, var

def plot(x, y, e):
    """this function create a defined graph with the data inputs"""

    plt.rcParams['text.usetex'] = True

    x = np.asarray(x)
    y = np.asarray(y)
    e = np.asarray(e)

    fig, (ax1) = plt.subplots(1)

    # ax1.set_xlabel('Frequency [Hz]')
    # ax1.set_ylabel('', color='r')
    # ax1.set_title("Output PLL",  fontsize=20)
    # ax1.plot(bins, out, color='r', scalex=True, scaley=True)
    # ax1.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_out), horizontalalignment='right', verticalalignment='top',color='m',transform=ax1.transAxes)
    # ax1.tick_params(axis='y', labelcolor='red')
    # ax1.grid(True)
    plt.errorbar(x, y, e, linestyle='None', marker='^')

    plt.show()
    # ax2.set_xlabel('Frequency [Hz]')
    # ax2.set_ylabel('Power [dB]', color='r')
    # ax2.set_title("Input PLL",  fontsize=20)
    # ax2.plot(bins, src, color='r', scalex=True, scaley=True)
    # ax2.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_src), horizontalalignment='right', verticalalignment='top',color='m',transform=ax2.transAxes)
    # ax2.tick_params(axis='y', labelcolor='red')
    # ax2.grid(True)
    # fig.suptitle(name_test_usetex, fontsize=30)
    # fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    plt.show()

def main():
    size = 100
    samp = 1000
    repeat = 100
    x = []
    m = []
    v = []
    for freq in np.arange(-50.0, 50.0, 0.1):
        signal = sine(freq, samp, size * repeat)
        mean, var = groetzel(signal, 0, samp, size)
        v.append(var)
        m.append(mean)
        x.append(freq)
    plot(x,m,v)

if __name__ == "__main__":
    main()


    
    
