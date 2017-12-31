import sys
import os
import signal
import subprocess
import logging
from uuid import getnode, uuid4
from abc import ABC, abstractmethod
import time
import gc
import atexit
from functools import wraps

log = logging.getLogger(__name__)

def gc_decorator(critical_func):
  
    @wraps(critical_func)
    def wrapper(*args, **kwargs):
        gc.disable()
        # gc.disable() doesn't work, because some random 3rd-party library will
        gc.set_threshold(0)
        # Suicide immediately after other atexit functions finishes.
        # CPython will do a bunch of cleanups in Py_Finalize which
        # will again cause Copy-on-Write, including a final GC
        atexit.register(os._exit, 0)
        return critical_func(*args, **kwargs)
    return wrapper
        
        

class BaseNode(ABC):
    __slots__ = ['_platform_id', '_pid', '_uid', ]  # using slot to declare python object can allow as
    # control memory allocated and prevent adding additional attribute to an object later

    def __init__(self, name=None):
        super().__init__()      
        self._platform_id = getnode()
        self._pid = os.getpid()
        self._uid = '%s#%s@%s' % (
                str(uuid4()),
                __name__,
                ''.join(("%012X" % self._platform_id)[i:i + 2] for i in range(0, 12, 2))
            )
    
    @abstractmethod
    def init(self):
        """
        To avoid any device IO problem, retrieving data must be done outside the critical section;
        All initialization, loading data from disk or similar tasks must be done here
        :return:
        """
        log.debug('Initializing Node ...')
        return 0

    @abstractmethod
    def run(self):
        """
        Code to be executed by the Node
        :return:
        """
        log.debug('starting execution of node ...')
        return 0

    @abstractmethod
    def finalize(self):
        """
        To avoid any device IO problem, writing data must be done outside the critical section;
        All finalization, writing data to disk or similar tasks must be done here
        :return:
        """
        log.debug('Finalizing the Node ...')
        return 0
            
    @gc_decorator
    def _execute(self):
        self.init()
        self.run()
        self.finalize()
        
class RTNode(BaseNode):
    def init(self):
        return 0
    
    def run(self):
        print("Node running.....")
        return 0
    
    def finalize(self):
        return 0
        
if __name__ == "__main__":
    mynode = RTNode()
    mynode._execute()