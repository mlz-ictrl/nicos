#!/usr/bin/python
# fft sine shift test for cascade viewer
# author: tweber

import numpy as np
from scipy.fftpack import *
import matplotlib.pyplot as plt

samples = 64
omega = 1       # num_osc

amp = 2
offs = 5
phase = 0
shift = np.pi+1.

k = np.linspace(0, samples-1, samples)
t = np.linspace(0, 2.*np.pi, samples)
y = amp*np.sin(omega*t + phase) + offs
#print 'y = ' + str(y)

shift_samples = shift/(2.*np.pi) * samples

y_fft = fft(y)
#y_fft_shift = y_fft * np.exp(-1j * 2.*np.pi*k/samples * shift_samples)

y_fft_shift = np.zeros(samples, dtype=np.dtype(complex))
y_fft_shift[omega] = y_fft[omega]*2
y_fft_shift[omega] *= np.exp(-1j * 2.*np.pi/samples * shift_samples)

# offset
y_fft_shift[0] = np.real(y_fft[0])

y_ifft = ifft(y_fft_shift)

#print 'Re(y_ifft) = ' + str(np.real(y_ifft))
#print 'offs = ' + str(y_fft_shift[0]/samples)

#print np.angle(y_fft[omega]) + np.pi/2 - 0.5/samples * 2.*np.pi


plt.figure()
plt.plot(t, y, 'o-', label='original')
plt.plot(t, np.real(y_ifft), 'o-', label='shifted')
plt.grid(True)
plt.legend(loc='best')

plt.figure()
plt.plot(t, np.real(y_fft), 'o-', label='fft, real, original')
plt.plot(t, np.real(y_fft_shift), 'o-', label='fft, real, shifted')
plt.grid(True)
plt.legend(loc='best')

plt.figure()
plt.plot(t, np.imag(y_fft), 'o-', label='fft, imag, original')
plt.plot(t, np.imag(y_fft_shift), 'o-', label='fft, imag, shifted')
plt.grid(True)
plt.legend(loc='best')

plt.show()
