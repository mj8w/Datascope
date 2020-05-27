"""
This file is stored in the Version Control System. The intended purpose is to copy this file to config.py
    and modify it for your use.
"""

config = {
    # number of signals possibly shown. If increased, code modifications have to be made to add the plot curves (in datascope)
    "max_signal_count":4,

    # classes available are "CSV_Buffer", and "DecodeBinary"
    # it is recommended that you copy one of these classes and change it's name to create your own decoder
    # See any of the "get_xxx.py" files for the definitions of these classes
    # and modify it to meet your specific needs. You will need to import the new class in datascope.py
    "InputClass":"CSV_Buffer",

    # all of the possible signals must be defined even if they aren't being used.
    # colors are those acceptable to pyqtgraph.mkColor()
    # width and precision are arguments for string formatting of the crosshairs statistics
    # kwargs can be found in the library - site-packages\pyqtgraph\graphicsItems\PlotDataItem.py 
    "signals":[
        {"name":"Red", "color":"FF0000", "width":4, "precision":2, "scale":1.0 },
        {"name":"Blue", "color":"0000FF", "width":4, "precision":4, "scale":1.0, "kwargs":{"symbolBrush":(0,0,255)}},
        {"name":"Green", "color":"00FF00", "width":0, "precision":2, "scale":1.0 },
        {"name":"Yellow", "color":"FFFF00", "width":0, "precision":2, "scale":1.0 },
    ],

    # default settings of check boxes
    "grids_checked":True,
    "xhairs_checked":True,
}

import logging
def logset(logname):
    ''' convenience sets up a logger object pre-configured with default functions
        attached to the logtype. That way you can set up all the log functions that 
        will use the logtype in one line. Usually, you will use one log type per file.
        You also need to set up the log type in logging.ini.
    Usage:
        from <project> import logset
        debug, info, warn, err = logset('<logtype name>')
    '''
    llog = logging.getLogger(logname)
    llog.propagate = False
    return (llog.debug, llog.info, llog.warning, llog.error)
