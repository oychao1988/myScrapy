import os
import socket
import gevent
from gevent import monkey
monkey.patch_all()

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class HttpServer(object):
    def __init__(self, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        host = ('', port)
        server_socket.bind(host)
        self.server_socket = server_socket

    def request_handler(self, service_client_socket, client_addr):
        request_data = service_client_socket.recv(1024)
        response_line = 'HTTP/1.1 %s\r\n' % 200
        headers = {'Host': 'ProxyTestServer'}
        response_header = '%s: %s\r\n' % ('Host', headers['Host'])
        response_body = 'client_addr: {}'.format(client_addr)
        response_data = (response_line + response_header + '\r\n' + response_body).encode('utf-8')
        service_client_socket.send(response_data)
        service_client_socket.close()
        print(client_addr, '已断开')

    def start(self):
        self.server_socket.listen(128)
        print('服务器已开启')
        while True:
            service_client_socket, client_addr = self.server_socket.accept()
            print(client_addr, '已连接')
            gevent.spawn(self.request_handler, service_client_socket, client_addr)

def start_forever(port=8080):
    hs = HttpServer(port)
    hs.start()

if __name__ == '__main__':
    start_forever()