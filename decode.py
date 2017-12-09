#!/usr/bin/env python3

import os
import sys
import numpy as np
import wave

def sample_falling(clk, data):
	falling = (clk[:-1] & ~clk[1:]).astype(np.bool)
	return data[1:][falling]

def kfloor(n, k):
	return n // k * k

if __name__ == '__main__':
	infile = sys.argv[1]
	inname = os.path.splitext(infile)[0]

	D = 20 # reduce sample rate by this factor
	fs = 1e6 # input sample rate
	fd = fs / D # output/decimated sample rate

	a = np.fromfile(infile, dtype=np.uint8)
	b = np.unpackbits(a).reshape((-1, 8))
	clk = b[:,6]
	data = b[:,7]

	samples = sample_falling(clk, data)

	# let's turn ones into +1 and zeros into -1
	samples = samples.astype(np.int8) * 2 - 1

	# https://tomroelandts.com/articles/how-to-create-a-simple-low-pass-filter
	fc = 20000 / fs # cutoff frequency, normalized to fs
	b = 0.2 * fc # transition width
	N = int(np.ceil(4/b)) # number of taps
	if N % 2 == 0: N += 1
	print(f'N = {N}')

	n = np.arange(N)
	h = np.sinc(2 * fc * (n - (N-1) / 2.0)) # sinc kernel
	w = 0.42 - 0.5*np.cos(2*np.pi * n / (N-1)) + 0.08 * np.cos(4 * np.pi * n / (N-1)) # blackman window
	h *= w # apply window
	h /= np.sum(h) # normalize

	filtered = np.convolve(samples, h)

	#filtered -= filtered.mean() # PDM might have a DC bias...

	# decimate
	output = filtered[::D]

	# cut off initial values where the filter had overhang
	#output = output[N//D+1:-N//D]

	output.astype(np.float32).tofile(f"{inname}-f32-{fd:.0f}.raw")

	with wave.open(f"{inname}-f32-{fd:.0f}.wav", mode='w') as fh:
		fh.setnchannels(1)
		fh.setsampwidth(2)
		fh.setframerate(fd) # decimated sample rate
		fh.writeframes((output * 2**15).astype(np.int16))
