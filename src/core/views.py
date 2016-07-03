import asyncio
import aiohttp_jinja2

from aiohttp.web import View


#@url_route('/hello/{name:\w+}')
class HelloWorldView(View):

    @asyncio.coroutine
    def get(self, request, name=None, *args, **kwargs):
        return u'Hello %s' % name


#url_route('/json')
class HelloWorldJsonView(View):

    @asyncio.coroutine
    def get(self, request, *args, **kwargs):
        return {'message': 'Hello! This is JSON'}


class StreamTemplateView(View):
    template = 'index.html'

@aiohttp_jinja2.template('index.html')
def index_handler(request):
    return {'name': 'World!!!'}

@aiohttp_jinja2.template('game.html')
def game_handler(request):
    return {'name': request.GET.get('name')}

@aiohttp_jinja2.template('gamepad.html')
def gamepad_handler(request):
    return {'name': request.GET.get('name')}