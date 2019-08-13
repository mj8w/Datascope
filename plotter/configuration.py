# -*- coding: utf-8 -*-
"""
Objects used in structured configuration file 
"""
            
class Signal():
    """Signal definition & characteristics """
    def __init__(self, range_x = [-1.0,1.0], color = "white", holdup = False, precision = ('b',7,0), _id = 0 ):
        self.range_x = range_x
        self.color = color
        self.holdup = holdup
        self.precision = precision
        self.id = _id
    def __repr__(self):
        return "%s(\n    range_x=%r,\n    color=%r,\n    holdup=%r,\n    precision=%r\n    ,id=%r\n    )" % (
            self.__class__.__name__, self.range_x, self.color, self.holdup, self.precision, self.id)
       
def as_string(cfg):
    cfg_str = ["""from configuration import Signal\n\nconfiguration = {\n"""]
    for k in cfg:
        v = cfg[k]
        cfg_str.append('"{}":{},\n'.format(k,v))
    cfg_str.append("}")
    return("".join(cfg_str))

def write_config(cfg):
    """ Write the configuration to config.py """
    
    with open("config.py", "w") as file:
        file.write(self.as_string())
    