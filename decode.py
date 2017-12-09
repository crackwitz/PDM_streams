#!/usr/bin/env python3

import os
import sys
import numpy as np

def sample_falling(clk, data):
	falling = (clk[:-1] & ~clk[1:]).astype(np.bool)
	return data[1:][falling]

def kfloor(n, k):
	return n // k * k

if __name__ == '__main__':
	infile = sys.argv[1]
	inname = os.path.splitext(infile)[0]

	D = 20
	fs = 1e6
	fd = fs / D

	a = np.fromfile(infile, dtype=np.uint8)
	b = np.unpackbits(a).reshape((-1, 8))
	clk = b[:,7]
	data = b[:,6]

	samples = sample_falling(clk, data)

	#N = len(samples)
	#bits = 6
	#(samples[:kfloor(N, 2**bits)].reshape((-1, 2**bits)).sum(axis=1) - 2**(bits-1)) \
	#.astype(np.int8) \
	#.tofile(f"{inname}-{bits}bit.raw")
	#print(1e6 / 2**bits)


	# https://tomroelandts.com/articles/how-to-create-a-simple-low-pass-filter
	fc = 20000 / fs
	b = 0.2 * fc
	N = int(np.ceil(4/b))
	if N % 2 == 0: N += 1
	print(f'N = {N}')

	n = np.arange(N)
	h = np.sinc(2 * fc * (n - (N-1) / 2.0))
	w = 0.42 - 0.5*np.cos(2*np.pi * n / (N-1)) + 0.08 * np.cos(4 * np.pi * n / (N-1))
	h *= w
	h /= np.sum(h)

	filtered = np.convolve(samples, h)
	filtered -= filtered.mean()

	filtered[::D].astype(np.float32).tofile(f"{inname}-f32-{fd:.0f}.raw")
