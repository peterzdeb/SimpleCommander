import asyncio
import json
import logging
from datetime import datetime
from random import randint, shuffle

from gamepad.unit import Unit


class GamepadController(object):
    _instance = None
    launched = False
    websockets = {}

    def __init__(self, height=None, width=None, invaders_count=None, notify_callback=print):
        self.units = {}
        self.notifier = notify_callback

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GamepadController, cls).__new__(cls)
        return cls._instance

    def do_action(self, actions):
        self.notifier(actions)

    def new_unit(self, unit_class, *args, **kwargs):
        """ Create new unit. """
        kwargs['controller'] = self
        unit = unit_class(*args, **kwargs)
        self.units[unit.id] = unit
        unit.response('new')
        logging.debug('Create new unit - %s -', unit.__class__.__name__)
        return unit

    def drop_connection(self, socket):
        socket = self.websockets[id(socket)]
        self.remove_unit(socket['hero'])
        del socket

    @asyncio.coroutine
    def notify_clients(self, data):
        for key in self.websockets:
            if not self.websockets[key]['socket']._closed:
                self.websockets[key]['socket'].send_str(json.dumps(data))

    def cleanup_units(self, units):
        """ Remove list of units. """
        for unit in units:
            if unit.is_dead:
                self.remove_unit(unit.id)

    def remove_unit(self, unit_id):
        """ Remove unit with unit ID. """
        unit = self.units.get(unit_id)
        if unit:
            class_name = unit.__class__.__name__
            self.units[unit_id].response('delete')
            del self.units[unit_id]

    def start(self, socket, data, *args, **kwargs):
        my_hero = self.new_unit(Unit)
        self.websockets[id(socket)] = {'socket': socket, 'hero': my_hero.id}
        name = data.get('name', 'user')
        start_conditions = {'init': {
            'unit_id': my_hero.id,
            'units': self.get_units()}}
        socket.send_str(json.dumps(start_conditions))

    def get_units(self):
        if len(self.units):
            return {unit: self.units[unit].to_dict() for unit in self.units}
        return {}
