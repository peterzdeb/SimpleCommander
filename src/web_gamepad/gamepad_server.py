import asyncio
import configparser
import json
import logging
from aiohttp import server, web, MsgType

import os
import aiohttp_jinja2
import jinja2

from web_gamepad.core import views
from web_gamepad.gamepad.game_factory import get_game


class WebGamepadServer(object):
    _instance = None

    def __init__(self,  host=None, port=None,
                 templates=None, static_path=None, notify_callback=print,
                 **kwargs):
        logging.info('Init Server on host %s:%s' % (host, port))
        self._loop = asyncio.get_event_loop()
        self._app = web.Application(loop=self._loop)
        if not static_path:
            self._static_path = os.path.join(os.path.dirname(__file__), 'static')
        else:
            self._static_path = static_path
        if not templates:
            templates = os.path.join(os.path.dirname(__file__), 'templates')

        self._load_routes()
        self._load_static()
        self._controller = get_game(600, 800, 5, notify_callback)
        self._server = self._loop.create_server(self._app.make_handler(),
                                                host, int(port))
        if templates:
            aiohttp_jinja2.setup(self._app,
                                 loader=jinja2.FileSystemLoader(templates))
        self._app.router.add_route('*', '/index', views.index_handler)
        self._app.router.add_route('*', '/game', views.game_handler)
        self._app.router.add_route('*', '/', views.gamepad_handler)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebGamepadServer, cls).__new__(cls)
        return cls._instance

    def start(self):
        self._server = self._loop.run_until_complete(self._server)
        logging.info('Server has started.')

    def stop(self):
        self._server.close()
        logging.info('Server has stopped.')

    def _load_routes(self):
        self._app.router.add_route('GET', '/ws_stream', self.ws_stream)

    def _load_static(self):
        self._app.router.add_static('/static', self._static_path)

    @asyncio.coroutine
    def ws_stream(self, request, *args, **kwargs):
        ws = web.WebSocketResponse()
        ws.start(request)
        while not ws.closed:
            msg = yield from ws.receive()
            if msg.tp == MsgType.text:
                if msg.data == 'close':
                    yield from ws.close()
                    self._controller.drop_connection(ws)
                else:
                    data = json.loads(msg.data)
                    if 'start' in data:
                        self._controller.start(ws, data['start'])
                    else:
                        yield from self._controller.do_action(**data)
            elif msg.tp == MsgType.close:
                logging.info('websocket connection closed')
                self._controller.drop_connection(ws)
            elif msg.tp == MsgType.error:
                logging.info('ws connection closed with exception %s', 
                    ws.exception())
                self._controller.drop_connection(ws)

        return ws


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('WebGamepad')
    config = configparser.ConfigParser()
    config_file = os.path.join(os.getcwd(),
                               'etc', 'command_server.conf')
    log.info('Using Configuration file: %s' % config_file)
    config.read(config_file)
    host = config.get('commandServer', 'host')
    port = os.environ.get('PORT', config.get('commandServer', 'port'))
    static_path = config.get('commandServer', 'static_path')
    templates = config.get('commandServer', 'templates')
    loop = asyncio.get_event_loop()
    server = WebGamepadServer(host=host, port=port, templates=templates)#, static_path=static_path)
    try:
        server.start()
        loop.run_forever()

    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()
