from datetime import datetime

from werkzeug.exceptions import HTTPException, BadRequest
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

import tables #snatches, status
from utils import ParameterError, required_params


class Leonidas(object):

    def __init__(self):
        self.url_map = self.get_url_map()
        self.config = self.load_config()
        tables.bind(self.config['database'])

    @required_params('info_hash', 'peer_id', 'ip', 'port')
    def announce(self, user_token, info_hash, peer_id, ip, port,
                 uploaded=0, downloaded=0, left=0, compact=False,
                 no_peer_id=False, event=None, numwant=50,
                 key=None, trackerid=None):
        return Response('Hello %s' % user_token)

    def announce_formatter(self, request, user_token):
        ip = request.args.get('ip') or request.remote_addr
        return dict(request.args, user_token=user_token, ip=ip)
        
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            formatted = getattr(self, endpoint + '_formatter')(request, **values)
            return getattr(self, endpoint)(**formatted)
        except HTTPException, e:
            return e
        except ParameterError, e:
            return BadRequest(description=unicode(e))

    def get_url_map(self):
        return Map([
            Rule('/<user_token>/announce', endpoint='announce'),
        ])
        
    def load_config(self):
        return {}

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, *args, **kwargs):
        return self.wsgi_app(*args, **kwargs)


def create_app(app_class, config=None):
    if config is None:
        config = {}        
    app = app_class()
    app.configure(config)
    return app


def main(host='0.0.0.0', port=5000):
    from werkzeug.serving import run_simple
    app = create_app(Leonidas)
    run_simple(host, port, app, use_debugger=True, use_reloader=True)

if __name__ == '__main__':
    main()        
