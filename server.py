from socket import *
import threading
import sys
from time import gmtime, strftime
from manage_data import *
import os
import gzip
import base64
import zlib
import manage_data
import log

threads = []
PORT = sys.argv[1]

STATUS_CODES = {
    100: 'Informational',
    200: 'OK',
    201: "Created",
    300: 'Redirection',
    304: 'Not Modified',
    400: 'Bad Request',
    404: 'Not Found',
    500: 'Server-Error'
}
files = {'/': "src/index.html"}

CONTENT_TYPE = {
    "html": "text/html; charset=UTF-8;",
    "jpeg": "image/jpeg",
    "ico": "image/jpeg",
    "jpg": "image/jpeg",
    "json": "application/json; charset=utf-8;",
    "js": "text/javascript; charset=UTF-8",
    None: None
}


def print_linebreak():
    print(
        "\n\n-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
    )
    print()


class Parser:
    def __init__(self):
        self.msg_body = None
        self.headers = None
        self.res_body = None
        self.queries = {}
        self.cookies = None
        self.req_headers_general = {
            "method": None,
            "uri": None,
            "protocol": None,
            "Request URL": None,
            "User-Agent": None,
            "Cookie": None,
            "If-Modified-Since": None
        }
        self.respnose = None
        self.res_headers = {
            "Date": None,
            "Server": None,
            "Content-encoding": None,
            "Content-type": "text/html; charset=utf-8",
            "Set-cookie": None,
            "Expires": None,
            "Content-Length": None,
            "Content-language": 'en',
            'Status': None,
            'Last-Modified': None,
            'Connection': "Close"
        }

    def return_CRLF(self, msg):
        return msg.split("\r\n")

    def return_SP(self, msg):
        return msg.split(' ')

    def return_LWS(self, msg):
        return msg.split('\r\n, ')

    def extract_msg(self, msg):
        msg = msg.split('\r\n\r\n', 1)
        # print("in extract_msg: msg: ")
        count = 1
        # for i in msg:
        #     print(count, i)
        #     count += 1
        self.headers = msg[0]
        if len(msg) >= 2:  # if len=2: request contains both headers and body
            self.msg_body = msg[1]
        if self.msg_body:
            print("in extract_msg: len(self.msg_body):  ", len(self.msg_body))
        else:
            print("in extract_msg:request body is empty")
        # print("in extract_msg: self.msg_body: ", self.msg_body)
        # if len(msg) > 2:
        # self.res_headers['Status'] = 400  # bad request
        return

    def extract_headers(self):
        self.headers = self.headers.split('\r\n')
        try:
            self.req_headers_general['method'], self.req_headers_general[
                'uri'], self.req_headers_general['protocol'] = self.headers[
                0].split(' ')
        except:  # invalid syntax
            self.res_headers['Status'] = 400  # bad request
            return

        try:
            self.req_headers_general['uri'], queries = self.req_headers_general['uri'].split(
                '?')
            try:
                queries = queries.split('&')
                for query in queries:
                    try:
                        attr, value = query.split('=')
                        self.queries[attr] = value
                    except:
                        self.res_headers['Status'] = 400
                        return
            except:
                self.res_headers['Status'] = 400
        except:
            self.queries = {}

        # print("in extract_headers => self.queries : ", self.queries)
        self.headers = self.headers[1:]
        for key_value in self.headers:
            attr, value = key_value.split(': ')
            self.req_headers_general[attr] = value

    def print_headers(self):
        print("Headers:")
        for attr in self.req_headers_general:
            print(attr, "\t\t: ", self.req_headers_general[attr])
        print()

    def print_msg_body(self):
        print("Msg Body:\n")
        print(self.msg_body)

    def add_res_headers(self, response):
        for attr in self.res_headers:
            if self.res_headers[attr]:
                response += "{}: {}\r\n".format(attr,
                                                str(self.res_headers[attr]))
        return response

    def print_res_headers(self, msg):
        print("\n************************     response headers: Start    *****************")
        print(msg)
        print("************************     response headers: End    *****************")
        return

    def resolve_uri(self, uri):  # returns (file_path, file_extension, status_code)
        print("in resolve_uri():\ninitial URI: " + uri)
        # print("quries: ", self.queries)
        method = self.req_headers_general['method']
        root = "src"
        # if request method is GET
        if method in ["GET", "HEAD"]:

            if uri == "/":
                # print("Path exits")
                path = "src/index.html"
                file_extention = "html"
                return (path, file_extention, 200)
            if uri == "/data":
                path = "src/data/data_file1.json"
                file_extention = "json"
                return (path, file_extention, 200)
            # root directory is "src"
            uri = uri.strip('/')
            # if url has some extension like .json, .php,.html, .js, .jpeg
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
                uri += "/index.html"
                file_extention = "html"
            # path will contain predicted path by joining root_directory and uri
            path = os.path.join(root, uri)
            print("path: ", path)
            print("file_extension: ", file_extention)
            # if file exits, return 200 OK
            if os.path.isfile(path):
                return (path, file_extention, 200)
            # file does not exit, return 404
            else:
                return (path, file_extention, 404)

        if method == "POST":
            if uri == "/data":
                path = "src/data/data_file1.json"
                file_extention = "json"
                return (path, file_extention, 200)
            uri = uri.strip('/')
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
            path = os.path.join(root, uri)
            return (path, file_extention, 200)

        if method == "PUT":
            uri = uri.strip('/')
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
            path = os.path.join(root, uri)
            return (path, file_extention, 200)

        if method == "DELETE":
            uri = uri.strip('/')
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
            path = os.path.join(root, uri)
            if os.path.isfile(path):
                return(path, file_extention, 200)
            else:
                return(path, file_extention, 404)

    def create_response(self):
        # Defining response headers (which will always be sent)
        self.res_headers["Date"] = strftime("%a, %d %b %Y %H:%M:%S GMT",
                                            gmtime())
        self.res_headers["Server"] = "localhost"

        method, URI, http_version = self.req_headers_general[
            'method'], self.req_headers_general[
                'uri'], self.req_headers_general["protocol"]

        # status_code is None at this moment unless it is 400
        status_code = self.res_headers['Status']

        # Check if the request format is valid. If valid Move Further
        # Else return 400 response
        if self.res_headers['Status'] == 400:
            response = "{} {} {}\r\n".format(str(http_version), 400,
                                             STATUS_CODES[400])  # Status line
            response = self.add_res_headers(response)
            response += "\r\n400 Bad Request\r\n"
            self.print_res_headers(response)
            return response.encode()

        # file_path, file_extention, status_code = self.resolve_uri(URI)
        # reason_phrase = STATUS_CODES[status_code]
        # self.res_headers["content-encoding"] = "br"

        if method in ["GET", "HEAD"]:
            file_path, file_extention, status_code = self.resolve_uri(URI)
            reason_phrase = STATUS_CODES[status_code]
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             reason_phrase)  # Status line

            self.res_headers['Status'] = status_code
            # if request is valid but status code != 200
            # i.e  404 Not Found, 403 Forbidden
            if status_code != 200:
                response = self.add_res_headers(response)
                self.print_res_headers(response)
                if status_code == 404:
                    if method == "GET":
                        response += "\r\n" + "404 Page Not Found\r\n"
                    return response.encode()
                else:
                    if method == "GET":
                        response += "\r\n" + "Not 200 Not Okay\r\n"
                    return response.encode()

            if file_extention in ["ico", "jpeg", "jpg"]:
                print("file extention is : " + str(file_extention))
                # print("starting image proceesing")
                # file_obj = open(file_path, 'rb')
                # image_raw = file_obj.read()
                self.res_headers['Last-Modified'], self.res_body = get_data(
                    file_path, file_extention, self.queries)

                if self.res_headers['Last-Modified'] == self.req_headers_general['If-Modified-Since']:
                    print("not modified image")
                    status_code = 304
                    self.res_headers['Status'] = status_code
                    response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                     STATUS_CODES[status_code])  # Status line
                    response = self.add_res_headers(response)
                    response += "\r\n"
                    self.print_res_headers(response)
                    return response.encode()

                print(" modified image")
                self.res_headers["Content-Length"] = len(self.res_body)
                self.res_headers["Accept-ranges"] = "bytes"
                self.res_headers["Content-type"] = CONTENT_TYPE[file_extention]

                response = self.add_res_headers(response)
                response.strip()
                self.print_res_headers(response)
                response += "\r\n"

                # encode headers (text); do not encode image_raw as it is binary
                response = response.encode()
                # self.res_body = image_raw
                # response += image_raw

                ###
                # with open(file_path, "r") as f:
                if method == "GET":
                    response += self.res_body
                ###
                return response

            elif file_extention in ["html", "json", "js"]:
                print("file extension is: " + str(file_extention))
                # with open(file_path, "r") as f:
                # html_data = f.read()
                # self.res_body = get_data(file_path, self.queries, file_extention)
                # self.res_body = html_data
                # print(self.res_body)

                ###
                self.res_headers['Last-Modified'], self.res_body = get_data(
                    file_path=file_path, file_extension=file_extention, queries=self.queries)

                if self.res_headers['Last-Modified'] == self.req_headers_general['If-Modified-Since']:
                    status_code = 304
                    self.res_headers['Status'] = status_code
                    response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                     STATUS_CODES[status_code])  # Status line
                    response = self.add_res_headers(response)
                    response += "\r\n"
                    self.print_res_headers(response)
                    return response.encode()
                ###
                if self.res_body:
                    self.res_headers["Content-type"] = CONTENT_TYPE[file_extention]
                    self.res_headers["Content-Length"] = len(self.res_body)

                # print("Adding headers by add_res_headers")
                response = self.add_res_headers(response)
                self.print_res_headers(response)
                if method == "GET":
                    if self.res_body:
                        response += "\r\n" + self.res_body + "\r\n"
                elif method == "HEAD":
                    response += "\r\n"
                response = response.encode()
                # encode whole response(headers+body) as everything is textual
                return response

            # if file extension is not recognizable. Return Bad Request
            elif file_extention:
                response = "{} {} {}\r\n".format(str(http_version), 400,
                                                 STATUS_CODES[400])  # Status line
                if method == "GET":
                    response += "\r\nExtenstion Of File not recognizable. So Bad Request 400\r\n"
                self.print_res_headers(response)
                return response.encode()

        # method other than GET
        elif method == "POST":
            print("in Create_response(): method: POST")
            file_path, file_extention, status_code = self.resolve_uri(URI)
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             STATUS_CODES[status_code])  # Status line
            self.res_headers['Status'] = status_code

            # if self.req_headers_general["Content-Type"] == "application/x-www-form-urlencoded":
            # print(
            # "in POST method application/x-www-form-urlencoded: msg_body\n" + self.msg_body)

            print("calling post_data()")
            status_code = post_data(uri=file_path, msg_body=self.msg_body,
                                    file_extension=file_extention, content_type=self.req_headers_general["Content-Type"])
            print("out of post_data()")
            response = self.add_res_headers(response)
            response += "\r\n" + "POST Successful"
            self.print_res_headers(response)
            return response.encode()

        elif method == "PUT":
            file_path, file_extention, status_code = self.resolve_uri(URI)
            print("Calling manage_data.put_data")
            status_code = manage_data.put_data(uri=file_path, msg_body=self.msg_body, file_extension=file_extention,
                                               content_type=self.req_headers_general["Content-Type"])
            print("Out of manage_data.put_data")
            print("method : PUT: ", file_path, file_extention, status_code)
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             STATUS_CODES[status_code])  # Status line

            if status_code == 200:
                self.res_body = "PUT OKAY\r\n"
            elif status_code == 201:
                self.res_body = "File Created\r\n"
            self.res_headers['Status'] = status_code
            self.res_headers["Content-Length"] = len(self.res_body)
            response = self.add_res_headers(response)
            self.print_res_headers(response)
            response += "\r\n" + self.msg_body
            return response.encode()

        elif method == "DELETE":
            file_path, file_extention, status_code = self.resolve_uri(URI)
            print("method : DELETE: ", file_path, file_extention, status_code)

            if status_code != 200:
                response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                 STATUS_CODES[status_code])  # Status line
                self.res_body = STATUS_CODES[status_code]
                self.res_headers["Content-Length"] = len(self.msg_body)
                response = self.add_res_headers(response)
                response += "\r\n" + self.res_body
                return response.encode()

            print("Calling delete_data()")
            status_code = manage_data.delete_data(
                uri=file_path, file_extension=file_extention, queries=self.queries)
            print("After delete_data(): status_code: ", status_code)

            reason_phrase = STATUS_CODES[status_code]
            self.res_headers['Status'] = status_code
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             reason_phrase)  # Status line
            if status_code == 200:
                self.res_body = "File Successfully Removed\n"
            elif status_code == 400:
                self.res_body = "Do not give query strings for DELETE request for html, jpeg, png, jpg files\n"
            elif status_code == 500:
                self.res_body = "Internal Server Error\n"

            self.res_headers["Content-Length"] = len(self.msg_body)
            response = self.add_res_headers(response)
            response += "\r\n" + self.res_body
            print("Response : ")
            self.print_res_headers(response)
            return response.encode()

        else:
            file_path, file_extention, status_code = self.resolve_uri(URI)
            status_code = 400
            self.res_headers['Status'] = status_code
            reason_phrase = STATUS_CODES[status_code]
            response = "{} {} {}".format(str(http_version), 400, reason_phrase)
            # self.res_headers(response)
            response = self.add_res_headers(response)
            response += "\r\n"
            self.print_res_headers(response)
            return response.encode()

    def set_cookie(self, keys_values):
        print("in set_cookie: ")
        # print(keys_values)
        try:
            for key in keys_values:
                self.respnose += 'Set-Cookie: {}={}\r\n'.format(
                    key, keys_values[key])
        except:
            pass
        # print(msg)


class Server():
    def __init__(self, host, port):
        # Parser.__init__(self)
        self.port = port
        self.host = host

    def start_server(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print("server running on port " + str(self.port))


class ClientThread(threading.Thread, Parser):
    def __init__(self, ip, port, client_socket):
        Parser.__init__(self)
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.client_socket = client_socket
        # print("New server socket thread started " + str(ip) + ":" + str(port))

    def run(self):
        # while True:
        """ iso-8859-1 decoding to decode image(binary files without any issues) """
        msg = self.client_socket.recv(4096000009).decode("iso-8859-1")
        """
            If msg is None... For now sendd 400
        """
        if msg == None:
            self.res_headers['Status'] = 400
            self.process_query()
            self.client_socket.close()

        print("****************************  Request msg: Start  ********************")
        print(msg)
        print("*****************************   Request msg: end   ********************\n")
        self.extract_msg(msg)
        # print("****************************  Request Headers: Start  ********************")
        # print(self.headers)
        # print("************************   Request Headers: end   ********************\n")
        self.extract_headers()
        # if self.res_headers['Status'] == 400: #400 Bad Request
        self.process_query()
        self.client_socket.close()
        request_line = self.req_headers_general['method'] + " " + \
            self.req_headers_general['uri'] + " " + \
            self.req_headers_general['protocol']
        log.access_log(status_code=self.res_headers["Status"], size=self.res_headers["Content-Length"], request_line=request_line,
                       client_ip=self.ip, user_agent=self.req_headers_general['User-Agent'])
        print_linebreak()

    def process_query(self):
        response = self.create_response()
        self.client_socket.send(response)
        return


if __name__ == "__main__":
    port = int(sys.argv[1])
    http_server = Server('', port)
    http_server.start_server()
    print_linebreak()
    while True:
        (client_socket, (ip, port)) = http_server.server_socket.accept()
        newClientThread = ClientThread(ip, port, client_socket)
        threads.append(newClientThread)
        # print("total sockets: " + str(len(threads)) + "\tcount: " +
        #       str(threading.active_count()))
        newClientThread.start()

    for t in threads:
        t.join()
