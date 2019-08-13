'''
Created on Jun 27, 2019

@author: Owner
'''
import struct, 
import regex as re


inpath = r"C:/Users/Owner/Downloads/Kalispell Antique Mall Inventory.wps"
workpath = r"C:/Users/Owner/Desktop/KAMI work.txt" 
outpath = r"C:/Users/Owner/Desktop/KAMI.txt" 

def getbyte(f):
    rec = 'x'  # placeholder for the `while`
    while rec:
        rec = f.read(1)
        if rec: 
            yield rec


#      Item                                            Paid               List                                                   



def main():
    
    with open(inpath, 'rb') as infile, open(workpath, 'wb') as outfile:
        for rcvd in getbyte(infile):
            data = struct.unpack('B', rcvd)[0] 
            if data == 0:
                continue
            elif data == 0x0D:
                outfile.write(rcvd)
            elif data == 0x0A:
                outfile.write(rcvd)
            elif data == 0x09:
                outfile.write(rcvd)
            elif data == 0x19:
                outfile.write("'")
            elif data == 0x19:
                outfile.write("'")
            elif data < 0x20:
                continue
            elif data > 0x7F:
                continue
            else:
                outfile.write(rcvd)       

    with open(workpath, 'r') as infile, open(outpath, 'w') as outfile:
        for line in infile:
            re_item = re.compile("")
            
            outfile.write(line)       
 
        
if __name__ == '__main__':
    main()