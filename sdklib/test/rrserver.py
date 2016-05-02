import threading
import SocketServer
import hashlib


class RequestResponseHandler(SocketServer.BaseRequestHandler):

    REQUEST_RESPONSE_JSON = {}
    DEFAULT_RESPONSE = """HTTP/1.1 404 OK\n\n"""
    HTTP_200_OK_RESPONSE = """HTTP/1.1 200 OK\n\n"""

    @classmethod
    def add_request_response(cls, request, response=None):
        response = response or cls.HTTP_200_OK_RESPONSE

        processed_request = cls.process_request(request)
        cls.REQUEST_RESPONSE_JSON[processed_request] = response

    @classmethod
    def clear(cls):
        cls.REQUEST_RESPONSE_JSON = {}

    @staticmethod
    def clean_request(request):
        pr = ""
        req = request.replace('\r\n', '\n')
        lines = req.split('\n')
        for line in lines:
            if ("Host:" not in line and
                    "Accept:" not in line):
                pr += line + '\n'
        return pr[:-1]

    @classmethod
    def process_request(cls, request):
        cr = cls.clean_request(request)
        digest = hashlib.sha1(cr).hexdigest()
        return digest

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        processed_data = self.process_request(data)
        if processed_data in self.REQUEST_RESPONSE_JSON:
            response = self.REQUEST_RESPONSE_JSON[processed_data]
        else:
            response = self.DEFAULT_RESPONSE
        self.request.sendall(response)


class RRServerManager():
    _RRSERVER = None

    @staticmethod
    def add_request_response(request, response=None):
        RequestResponseHandler.add_request_response(request, response)

    @staticmethod
    def clear():
        RequestResponseHandler.clear()

    def start_rrserver(self, host='127.0.0.1', port=0):
        if not self._RRSERVER:
            self._RRSERVER = RRServer((host, port), RequestResponseHandler)
        ip, port = self._RRSERVER.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self._RRSERVER.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        return ip, port

    def close_rrserver(self):
        if self._RRSERVER:
            self._RRSERVER.shutdown()
            self._RRSERVER.server_close()


class RRServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    manager = RRServerManager()
