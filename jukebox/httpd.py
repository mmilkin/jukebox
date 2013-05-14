from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import LoopingCall
from klein import Klein


class Source(object):
    def __init__(self, playlist):
        self.playlist = playlist
        self.clients = []
        self.file = None
        self.start_new_file()
        self.playlist.add_listener(self.start_new_file)

    def start_background(self):
        self.lc = LoopingCall(self.process_file)
        self.lc.start(.25) # TODO: bit rate?

    def stop_background(self):
        self.lc.stop()

    def start_new_file(self):
        if not self.playlist.cur:
            self.file = None
            return
        if self.file:
            self.file.close()
        self.file = open(self.playlist.cur.path, 'rb')

    def add_client(self, client):
        self.clients.append(client)
        # burst some data at the client or keep latency low?

    def process_file(self):
        if not self.file:
            return

        data = self.file.read(1024 * 8)
        if not data:
            self.file = None
            self.playlist.advance()
            return

        self.send(data)

    def send(self, data):
        for client in self.clients:
            client.send(data)


class Client(object):
    def __init__(self, request):
        self.request = request
        self.request.setHeader('Content-Type', 'audio/mpeg')

    def send(self, data):
        self.request.write(data)


class Stream(Resource):
    def __init__(self, source, client_factory=None):
        if not client_factory:
            client_factory = Client
        self.client_factory = client_factory

        self.source = source

    def render_GET(self, request):
        client = self.client_factory(request)
        self.source.add_client(client)
        return NOT_DONE_YET


class HTTPd(object):
    app = Klein()

    def __init__(self, api_resource, stream_resource):
        self.api_resource = api_resource
        self.stream_resource = stream_resource

    @app.route('/stream', branch=True)
    def stream(self, request):
        return self.stream_resource

    @app.route('/api/', branch=True)
    def api(self, request):
        return self.api_resource

    @app.route('/', branch=True)
    def index(self, request):
        return File('./static')
