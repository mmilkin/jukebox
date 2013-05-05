from twisted.web.static import File
from klein import Klein


class HTTPd(object):
    app = Klein()

    def __init__(self, api_resource):
        self.api_resource = api_resource

    @app.route('/api/', branch=True)
    def api(self, request):
        return self.api_resource

    @app.route('/', branch=True)
    def index(self, request):
        return File('./static')
