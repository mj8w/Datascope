
import logging
from logging import config as logging_config
logging_config.fileConfig('logging.ini', disable_existing_loggers = False)

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

class NoConfig(Exception):
    """ Exception for when config file is missing - which is the normal case on first use. """

    def __str__(self):
        return "Copy config_default.py to config.py, you can modify config.py to meet your needs."
