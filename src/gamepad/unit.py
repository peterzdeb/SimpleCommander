"""Base module for all units. """
import asyncio
import logging
import math
import uuid
from datetime import datetime

from simple_commander.utils.float_range import float_range
from simple_commander.utils.constants import ACTION_INTERVAL, MAX_ANGLE, MAX_SPEED, STEP_INTERVAL, UNIT_PROPERTIES
from simple_commander.utils.line_intersection import object_intersection, point_distance


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
        for attr in self.__dict__:
            if attr in UNIT_PROPERTIES:
                result[attr] = self.__dict__[attr]
        return result

    def reset(self):
        raise NotImplementedError

    def kill(self):
        logging.debug('Killing - %s ' % self.__class__.__name__)
        self.is_dead = True
