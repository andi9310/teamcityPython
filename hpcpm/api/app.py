import time

from flask import Flask, request
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from hpcpm.api import log
from hpcpm.api.helpers.database import database
from hpcpm.api.resources.ApiSpec import ApiSpec

flask_app = Flask(__name__)  # pylint: disable=invalid-name


def initialize(config):
    database.configure(config['database'])
    log.info(database)  # to avoid 'unused variable' warning :D
    api_spec = ApiSpec(config['host'])
    flask_app.register_blueprint(api_spec.blueprint, url_prefix='/api/hpcpm')


def run(port):
    http_server = HTTPServer(WSGIContainer(flask_app))
    http_server.bind(port, '0.0.0.0')
    log.debug('HTTP server starting')
    http_server.start(5)
    IOLoop.instance().start()


@flask_app.before_request
def start_request(*_):
    request.real_ip = request.headers.get('X-Real-Ip', request.remote_addr)
    request.start_time = time.time()

    log.info('REQUEST STARTED: %s %s %s', request.real_ip, request.method, request.url)


@flask_app.after_request
def end_request(response_class):
    response_class.headers.add('Access-Control-Allow-Origin', '*')
    response_class.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
    response_class.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    request.end_time = time.time()
    request_processing_time = '{0:.6f}'.format(request.end_time - request.start_time)

    log.info('REQUEST FINISHED (took %s seconds): %s %s %s', request_processing_time, request.real_ip,
             request.method, request.url)
    return response_class
