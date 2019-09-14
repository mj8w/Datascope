"""
This file is stored in the Version Control System. The intended purpose is to copy this file to config.py
    and modify it for your use.
"""

config = {
    # number of signals possibly shown. If increased, code modifications have to be made to add the plot curves (in live_data)
    "max_signal_count":4,

    # all of the possible signals must be defined even if they aren't being used.
    # colors are those acceptable to pyqtgraph.mkColor()
    # width and precision are arguments for string formatting of the crosshairs statistics
    "signals":[
        {"name":"Red", "color":"FF0000", "width":4, "precision":2, "scale":0.1 },
        {"name":"Blue", "color":"0000FF", "width":4, "precision":4, "scale":1.0 },
        {"name":"Green", "color":"00FF00", "width":0, "precision":2, "scale":1.0 },
        {"name":"Yellow", "color":"FFFF00", "width":0, "precision":2, "scale":1.0 },
    ],
}
