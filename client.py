import sys
from socket import *
from time import gmtime, strftime

host = '127.0.0.1'
port = int(sys.argv[1])

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((host, port))
print("clinet connected to port {}".format(port))


class client():
    def __init__(self):
        self.port = port
        self.http_version = None
        self.request = None
        self.request_uri = None,
        self.request_method = None
        self.request_line = None
        self.request_body = None
        self.request_headers = {
            "Date": None,
            "Connection": "close",
            "UserAgent": "Sarvesh's client code",
            "Cookie": None,
            "Accept-Encoding": None,
            "Accept-Language": None
        }

    def create_request(self):
        self.http_version = "HTTP/1.1"
        self.request_method = "GET"
        self.request_uri = "/"
        self.request_headers["Date"] = strftime(
            "%a, %d %b %Y %H:%M:%S GMT", gmtime())
        self.request = "{} {} {}\r\n".format(
            self.request_method, self.request_uri, self.http_version)
        for header in self.request_headers:
            if self.request_headers[header]:
                self.request += "{}: {}\r\n".format(
                    header, self.request_headers[header])
        self.request += "\r\n"
        if self.request_body:
            self.request += self.request_body
        print("************** self.request: start *************")
        print(self.request)
        print("**************** self.request: end **************")

    def listen(self):
        # while True:
        # try:
        msg = client_socket.recv(10000000).decode()
        print("Received msg by server: start")
        print(msg)
        print("Received msg by server: end")
        client_socket.close()
        # except:
        # pass

    def send_request(self):
        self.create_request()
        print("****************** Sending request: start ******************")
        client_socket.send(self.request.encode())
        print("****************** Sending request: end ******************")
        self.listen()


if __name__ == "__main__":
    print("In main")
    c = client()
    # c.create_request()
    c.send_request()
    # c.listen()
