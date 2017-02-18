"""Base module for all units. """
import asyncio
import logging
import math
import uuid
from datetime import datetime


class Unit(object):
    """ Base class for all the units. """

    def __init__(self, controller=None, *args, **kwargs):
        """ Basic initialization. """
        self.controller = controller
        self.time_last_calculation = datetime.now()
        self.id = str(uuid.uuid4())

    def response(self, action, **kwargs):
        if not self.controller:
            return
        data = {action: self.to_dict()}
        data[action].update(kwargs)
        asyncio.async(self.controller.notify_clients(data))

    def to_dict(self):
        result = {}
        return result

    def reset(self):
        raise NotImplementedError

    def kill(self):
        logging.debug('Killing - %s ' % self.__class__.__name__)
        self.is_dead = True
