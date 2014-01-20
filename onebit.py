#!/usr/bin/python
import wave
from struct import pack
from math import sin, pi
import random
import operator
import itertools

ONE = .5
ZERO = -.5

sample_rate = 22050

def write_samples(
    frequencies,
    weight_list=[[1.0]],
    decay=[1.0, .5, .25, .10],
    arpeggio_length=.02,
    length=int(sample_rate * 2),
    dithering=.0,
    channel_dithering=.0
):
    weight_list = weight_list or ([1.0 / len(frequencies)] * len(frequencies))
    num_arpeggio_stages = len(weight_list)
    print 'generating', frequencies, weight_list, len(weight_list)
    for i in xrange(length):
        time = float(i) / sample_rate
        arpeggio_stage = int(time / arpeggio_length) % num_arpeggio_stages
        assert 0 <= arpeggio_stage < num_arpeggio_stages

        values = []
        for f, d in zip(frequencies, decay):
            gain = 1 - (float(i) / length / d)
            assert gain <= 1
            if gain < 0:
                gain = 0
            dither_sample = random.gauss(0, channel_dithering)
            value = (sin(2 * pi * time * f) + dither_sample) * gain
            #print '%+10.4f' % value,
            
            values.append(value)
        #print

        sample = sum(v * w for v, w in zip(values, weight_list[arpeggio_stage]))

        #sample = reduce(operator.mul, values)
        #dither_sample = random.uniform(-dithering, dithering)
        dither_sample = random.gauss(0, dithering)
        #dither_sample = (i % 16) / 16.0

        #print '%15.3f' % sample
        sample = ONE if sample > dither_sample else ZERO

        byte = int(sample * 127) + 128
        if byte < 0: byte = 0
        if byte > 255: byte = 255

        file.writeframes(pack('B', byte))

chords = {
    'A': (440.0, 659.26, 880.0, 1046.5),
    'F#m': (369.99, 554.37, 739.99, 880.0),
    'Bm': (493.88, 739.99, 987.77, 1174.66),
    'D': (587.33, 880.0, 1174.66, 1479.98)
}

BEAT = int(sample_rate / 10)

file = wave.open('out.wav', 'w')
file.setnchannels(1)
file.setsampwidth(1)  # 8 bits
file.setframerate(sample_rate)

CHORD = [
    [.25, .25, .25, .25, .25],
]
MUTED = [
    [1.0, .5, .5, 0, 0]
]
ARPEGGIO = [
    [  .5, 1.0,  .0,  .0,  .0],
    [  .5,  .0, 1.0,  .0,  .0],
    [  .5,  .0,  .0, 1.0,  .0],
    [  .5,  .0,  .0,  .0, 1.0],
]

for i in range(2):
    dd = 0
    for chord in ('A', 'F#m', 'Bm', 'D'):
        freqs = chords[chord]
        if i != 0:
            freqs = (freqs[0] * .25,) + freqs
        else:
            freqs = freqs + (freqs[0] * 4,)

        write_samples(freqs, weight_list=CHORD,    length=2*BEAT, dithering=dd, channel_dithering=.1)
        write_samples(freqs, weight_list=MUTED,    length=2*BEAT, dithering=dd, channel_dithering=.0)

        write_samples(freqs, weight_list=ARPEGGIO, length=4*BEAT, dithering=dd, channel_dithering=.3)

        write_samples(freqs, weight_list=CHORD,    length=2*BEAT, dithering=dd, channel_dithering=.0)
        write_samples(freqs, weight_list=MUTED,    length=2*BEAT, dithering=dd, channel_dithering=.0)

        write_samples(freqs, weight_list=ARPEGGIO, length=4*BEAT, dithering=dd, channel_dithering=.3)

file.close()
