# -*- coding: utf-8 -*-
"""
create a hdf5 data file to use as an example of data input captured in plotter scope
"""

import sys
from time import time
from math import sin, pi
from numpy.random import random_sample  # @UnresolvedImport
from yaml import dump, YAMLObject # load
from struct import pack

from yaml_objs import Signal, Settings

precision = [
    ('h', 7, 8), # 16 bits, 1 sign, 7 bits whole, 8 bit fraction
    ('b', 3, 4),  # 8 bits, 1 sign, 3 bits whole, 4 bit fraction
    ('h', 15, 0), # 16 bits, 1 sign, 15 bits whole, 0 bit fraction
    ('h', 4, 13) # 16 bits, 1 sign, 4 bits whole, 13 bit fraction
    ]
def min_in_list(a):
    b = [i for i in range(len(a))]
    # Shell sort the contents of 'a', and keep the indices of what was sorted ('b').
    N = len(a)
    h=int(1)
    while h < N/3: h = int( 3*h + 1)
    while h >= 1:
        h = int(h)
        for i in range(h,N):
            j=i
            while j >= h and a[j] < a[int(j-h)]:
                x = a[j]        # exchange values
                a[j] = a[j-h]
                a[j-h] = x 
                x = b[j]        # exchange indices
                b[j] = b[j-h]
                b[j-h] = x 
                j -= h
        h /= 3
    return b[0]
                    
def signal(freq, amplitude, offset, noise, sample_rate, jitter):
    """ create a sine wave, with a bit of noise, and return samples at the
        sample rate +/- random jitter.
        This generates a point and the time of the next sample (so that multiple can be combined by caller) 
    """
    start_time = time()
    while(1):
        now = time() - start_time
        theta = now * 2 * pi * freq
        sample_noise = (-1 + (random_sample() * 2)) * noise
        value = (sin(theta) * (amplitude / 2)) + offset + sample_noise
        
        sample_jitter = (-1 + (random_sample() * 2)) * jitter
        next_time = now + sample_rate + sample_jitter
         
        yield (value, next_time)


def square(freq, amplitude, offset, noise, sample_rate, jitter):
    """ create a square wave, with a bit of noise. Set sample_rate at 2x frequency for
        samples only at the change
        This generates a point and the time of the next sample (so that multiple can be combined by caller) 
    """
    start_time = time()
    while(1):
        now = time() - start_time
        theta = now * 2 * pi * freq
        sample_noise = (-1 + (random_sample() * 2)) * noise
        sq = 1 if sin(theta) > 0 else -1
        value = (sq * (amplitude / 2)) + offset + sample_noise
        
        sample_jitter = (-1 + (random_sample() * 2)) * jitter
        next_time = now + sample_rate + sample_jitter
         
        yield (value, next_time)

        
MAX_SIGNALS = 16 # support up to 16 signals
        
def data_stream():
    """ Create an iterable stream with multiple signals, each with different scales and signal types.
        Used to create a very large file, with time stamps and which occur at slightly random time intervals.
        This will mimic the kind of data that we expect to capture.
    """
   
    # create generators of the source data
    sig = []
    sig.append(signal(200.,  54.,   7., 0.050, 1970.,  0.00768) ) # jitter corresponds to 15 chars at 115200 baud rate
    sig.append(signal(185.,   3.,  -3., 0.005, 1968.,  0.00768) ) 
    sig.append(signal(7.,   256., 128., 1.000, 1345.,  0.00768) ) 
    sig.append(square(133.,   1.,   1., 0.000, 133/2., 0.00768) )
     
    # time stamps of signals - list to determine which signal to record next 
    tm = [sys.float_info.max for _ in range(MAX_SIGNALS)]

    # data as recorded at this point...
    data = [0.0 for _ in range(MAX_SIGNALS + 1)] # +1 for the timestamp
    
    # update - bit mask of which signals were updated in this sample
    updated = 0

    # take the first samples so we can get the time-of-next-sample
    # Note: we could choose to throw the data samples out though, to test uninitialized data streaming 
    for sn in range(len(sig)):
        data[sn], tm[sn] = next(sig[sn])
        updated = 1<<sn
    yield (tm[sn], updated, data)
        
    # iterate progressively through the signals, taking the next sample available from whatever
    # source that might be (the lowest value of timestamp in tm[]) 
    # this might process the same stream over and over again, until some other "sample" is reported      
    for sn in range(len(sig),100000000):
        earliest = min_in_list(tm)
        timestamp = tm[earliest]  
        sampled = earliest
        updated = 1 << sampled          # set the type of data stored
        try:
            data[sampled], tm[sampled] = next(sig[sampled])
            yield (timestamp, updated, data)
        except StopIteration:
            break
        except IndexError:
            break

def binary_stream(n_samples):
    """ Create a binary interpretation of the data_stream, and yield bytes of encoded data """
    i_sample = 0
    for timestamp, updated, data in data_stream():
        bit = 0
        while updated > 0:
            if updated & 0x01:
                arg_type, _mant, fract = precision[bit]
                x = int(data[bit] * (2^fract))
                us = int(timestamp * 1e6)
                yield pack(">BI" + arg_type, 0xD5, us, x)    
            updated = updated >> 1
            bit += 1
        if i_sample > n_samples:
            break
        else:
            i_sample += 1
            
def main():
    """ Create a file with binary stream data like we might collect from an embedded target over a serial port.
        The first part will be a fixed length (16K) section of meta data text field
        everything after that is binary data like it was captured from a serial port
    """
    global precision
    
    signals = dump([
        Signal("sine1", precision = precision[0]), # sine1 has a range  
        Signal("sine2", precision = precision[1]), 
        Signal("sine3", precision = precision[2]), 
        Signal("square", precision = precision[3])])
    settings = dump(Settings(0.05))
    filler = "".join([" " for _ in range(16384 - (len(settings)+1 + len(signals)+1))])
    metadata = "\n".join([signals,settings,filler])
    
    with open("metatest.cpt", "wb") as f:
        f.write(bytes(metadata, 'utf-8'))
        f.write(b"".join([pkg for pkg in binary_stream(200)]))
    
if __name__ == "__main__":
    main()
