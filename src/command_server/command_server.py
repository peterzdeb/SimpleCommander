import aiohttp_jinja2
import asyncio
import configparser
import jinja2
import json
import logging
import src.core.views
import websockets

from aiohttp import web
from time import gmtime, strftime

from src.core.generic import routes
from src.simple_commander.controllers.main import GameController


class BaseCommandServer(object):

    def __init__(self, server_type=None, host=None, port=None, loop=None, templates=None):
        logging.info('Init %s Server on host %s:%s' % (server_type, host, port))
        self._server_type = server_type
        self._loop = loop or asyncio.get_event_loop()
        self._init_server(host, port)

        if templates:
            aiohttp_jinja2.setup(self._app, loader=jinja2.FileSystemLoader(templates))

    def start(self):
        self._server = self._loop.run_until_complete(self._server)
        logging.info(' %s has started.' % (self._server_type))

    def stop(self):
        self._server.close()
        logging.info('%s has stopped.' % (self._server_type))

    @classmethod
    def get_game_ctr(cls):
        if not cls._controller:
            cls._controller = GameController(50, 50, 2)
        return cls._controller


class StreamCommandServer(BaseCommandServer):
    _instance = None
    _controller = None

    def _init_server(self, host, port):
        self._app = web.Application(loop=self._loop)
        self._game = self.get_game_ctr()
        asyncio.async(self._game.run())
        self._server = websockets.serve(self.process_request, host, port)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StreamCommandServer, cls).__new__(cls)
        return cls._instance

    @asyncio.coroutine
    def process_request(self, websocket, path):
        self._game.set_hero()
        my_hero = self._game.units[-1]
        my_id = {'id': my_hero.id}
        yield from websocket.send(json.dumps(my_id))
        while True:
            if not websocket.open:
                break
            yield from websocket.send(self._game.get_field())
            yield from asyncio.sleep(1)
        yield from websocket.close()


class HttpCommandServer(BaseCommandServer):
    _instance = None

    def _init_server(self, host, port):
        self._app = web.Application()
        self._load_routes()
        self._load_static()
        self._server = self._loop.create_server(self._app.make_handler(),
                                                host, port)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HttpCommandServer, cls).__new__(cls)
        return cls._instance

    def _load_routes(self):
        logging.debug('Loading  Application Routes:\n%s' % '\n'.join(str(r) for r in routes.ROUTES))
        for route in routes.ROUTES:
            self._app.router.add_route(*route)

    def _load_static(self):
        self._app.router.add_static('/static', static_path)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('etc/command_server.conf')
    host = config.get('commandServer', 'host')
    http_port = config.get('commandServer', 'http_port')
    stream_port = config.get('commandServer', 'stream_port')
    static_path = config.get('commandServer', 'static_path')
    templates = config.get('commandServer', 'templates')
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    server = HttpCommandServer(server_type='Http Server', host=host, port=http_port, loop=loop, templates=templates)
    socket_server = StreamCommandServer(server_type='Stream Server', host=host, port=stream_port, loop=loop)
    try:
        server.start()
        socket_server.start()
        loop.run_forever()

    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        socket_server.stop()
        loop.close()