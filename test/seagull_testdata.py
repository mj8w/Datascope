from math import sin,pi
from itertools import izip
import matplotlib.pyplot as plt

    
def sin_signal(samples, freq, amplitude, offset = 0):  
    for x in samples:
        y =  sin(2. * pi * x * freq) * amplitude + offset 
        yield y


def lpf(samples, alpha):
    y = float(samples[0])
    for x in samples:
        y += alpha * float(x - y)
        yield y

if __name__ == '__main__':
    
    # create data for 10 seconds sampled at 100Hz - 
    # x is timing of each sample
    timespan = 10. # seconds
    sample_rate = 100. # hertz
    x = [x/sample_rate for x in range(0,int(sample_rate * timespan) + 1)]
    y1 = []

    for y1a, y1b, y1c in izip( 
        [y if y > 100 else 100 for y in sin_signal(x,0.3,100,100)],    # what we want to detect 
        sin_signal(x,1,10,20),      # drift of the sensor 
        sin_signal(x,0.01,50,100)):   # steady state of the wing
    
        y1.append(y1a + y1b + y1c)
    
    # use a low pass filter on the data to get baseline
    delta_t = 1./ sample_rate
    tau = 25
    alpha = delta_t / tau
#    y2 = [y for y in lpf(y1, alpha)]
    y2 = []
    # remove the baseline
    for f,y in izip(lpf(y1, alpha), y1):
        y2.append(y-f)

    fig, ax = plt.subplots()
    
    line1, = ax.plot(x, y1, label='incoming data')
    line2, = ax.plot(x, y2, dashes=[6, 2], label='baseline')
    
    ax.legend()
    plt.show()

    