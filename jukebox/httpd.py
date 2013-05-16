from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from klein import Klein


class Source(object):
    def __init__(self, playlist, encoder):
        self.playlist = playlist
        self.encoder = encoder
        self.clients = []
        self.playlist.add_listener(self.start_new_song)

    def start_new_song(self, event):
        if event != 'NEW_CUR':
            return
        if not self.playlist.cur:
            return
        self.encoder(
            song=self.playlist.cur,
            data_callback=self.send,
            done_callback=self.playlist.advance,
        )

    def add_client(self, client):
        self.clients.append(client)
        # burst some data at the client or keep latency low?

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
