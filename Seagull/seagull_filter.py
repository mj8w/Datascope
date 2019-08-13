import numpy as np
import matplotlib.pyplot as plt

def limit_change(data,allowed):
    """ Limit the amount of change within one sample to some slew rate """
    dnm1 = data[0]
    
    for d in data:
        if d - dnm1 < -allowed:
            newd = dnm1 - allowed
            yield(newd)
            dnm1 = newd
        elif d - dnm1 > allowed:
            newd = dnm1 + allowed
            yield(newd)
            dnm1 = newd
        else:
            yield(d)
            dnm1 = d

def limit_range(data,min_, max_):
    """ Limit the absolute range of samples to min/max values """
    for d in data:
        if d < min_:
            yield(min_)
        elif d > max_:
            yield(max_)
        else:
            yield(d)
    
if __name__ == '__main__':
    
    input_file_name = "C:\dev\Sloeber\Seagull\sample_data.txt"
    with open(input_file_name, "r") as input:
        data_str = input.read()
        data = []
        for line in data_str.split('\n'):
            if len(line):
                data.append(int(line))
    limited = [d for d in limit_range(data, -100, 100)]
    filtered = [d for d in limit_change(limited, 6)]
    
    x = [x/100. for x in range(0,101,1)]
    
    fig, ax = plt.subplots()
    
    line1, = ax.plot(x, data, label='Using set_dashes()')
    line2, = ax.plot(x, filtered, dashes=[6, 2], label='Using the dashes parameter')
    
    ax.legend()
    plt.show()

    