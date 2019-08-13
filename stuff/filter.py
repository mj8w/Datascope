import numpy as np
import matplotlib.pyplot as plt

def filter():
    # 
    pass

    
if __name__ == '__main__':
    
    input_file_name = "C:\dev\Sloeber\Seagull\sample_data.txt"
    with open(input_file_name, "r") as input:
        data_str = input.read()
        data = []
        for line in data_str.split('\n'):
            if len(line):
                data.append(int(line))
    filtered = filter(data)
    
    x = [x/100. for x in range(0,100,1)]
    
    fig, ax = plt.subplots()
    
    line1, = ax.plot(x, data, label='Using set_dashes()')
    line2, = ax.plot(x, data - 0.2, dashes=[6, 2], label='Using the dashes parameter')
    
    ax.legend()
    plt.show()

    