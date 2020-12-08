import signal
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
import mimetypes
import base64
from configparser import ConfigParser

# Server = None
# START = None
# PAUSE = None

SEREVR_STATE = "START"

config = ConfigParser()
config.read('config.ini')

admin_username = config['ADMIN']['username']
admin_username = admin_username.strip('"')
admin_password = config['ADMIN']['password']
admin_password = admin_password.strip('"')

documnetRoot = config['PATH']['documentRoot']
documnetRoot = documnetRoot.strip("'")
threads = []
# PORT = int(sys.argv[1])
PORT = int(config['DEFAULT']['port'])
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
logDir = config['LOG']['logDirectory']
logDir = logDir.strip("'")
max_thread_count = 0
STATUS_CODES = {
    100: 'Informational',
    200: 'OK',
    201: "Created",
    300: 'Redirection',
    304: 'Not Modified',
    400: 'Bad Request',
    401: "Unauthorized",
    403: 'Forbidden',
    404: 'Not Found',
    500: 'Server-Error',
    505: 'HTTP Version Not Supported'
}
files = {'/': "src/index.html"}

CONTENT_TYPE = {
    "html": "text/html; charset=UTF-8;",
    "jpeg": "image/jpeg",
    "ico": "image/jpeg",
    "jpg": "image/jpeg",
    "json": "application/json; charset=utf-8;",
    "js": "text/javascript; charset=UTF-8",
    "pdf": "application/pdf",
    "mp4": "video/mp4",
    None: None
}
# "application/pdf": "pdf",
# "video/mp4": "mp4"


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
        self.current_content_length = 0
        self.cumulative_content_length = 0
        self.total_content_length = 0
        self.queries = {}
        self.cookies = None
        self.req_headers_general = {
            "method": None,
            "uri": None,
            "protocol": None,
            "Request URL": None,
            "User-Agent": None,
            "Cookie": None,
            "If-Modified-Since": None,
            "Authorization": None
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
            'Connection': "Close",
            "Location": None
        }

    def return_CRLF(self, msg):
        return msg.split("\r\n")

    def return_SP(self, msg):
        return msg.split(' ')

    def return_LWS(self, msg):
        return msg.split('\r\n, ')

    def extract_msg(self, msg):
        try:
            msg = msg.split('\r\n\r\n', 1)
        except:
            self.res_headers['Status'] = 400
            return

        # print("in extract_msg: msg: ")
        self.headers = msg[0]
        if len(msg) >= 2:  # if len=2: request contains both headers and body
            self.msg_body = msg[1]
            self.current_content_length = len(self.msg_body)
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
            attr, value = key_value.split(': ', 1)
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
        if self.cookies:
            for attr in self.cookies:
                response += "Set-Cookie: {}={}\r\n".format(
                    attr, self.cookies[attr])

        return response

    def print_res_headers(self, msg):
        print("\n************************     response headers: Start    *****************")
        print(msg)
        print("************************     response headers: End    *****************")
        return

    def resolve_uri(self, uri):  # returns (file_path, file_extension, status_code)
        # print("in resolve_uri():\ninitial URI: " + uri)
        # print("quries: ", self.queries)
        method = self.req_headers_general['method']
        global documnetRoot
        """if request method is GET"""
        if method in ["GET", "HEAD"]:

            if uri == "/":
                # print("Path exits")
                path = os.path.join(documnetRoot, "index.html")
                file_extention = "html"
                if os.access(path, os.R_OK):
                    return (path, file_extention, 200)
                else:
                    return (path, file_extention, 403)
            if uri == "/data":
                path = "src/data/data_file1.json"
                path = os.path.join(documnetRoot, "data", "data_file1.json")
                file_extention = "json"
                if os.access(path, os.R_OK):
                    return (path, file_extention, 200)
                else:
                    return (path, file_extention, 403)
            """documnetRoot directory is "src"""
            uri = uri.strip('/')
            """ if url has some extension like .json, .php,.html, .js, .jpeg """
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
                uri += "/index.html"
                file_extention = "html"

            """ path will contain predicted path by joining documnetRoot_directory and uri"""
            path = os.path.join(documnetRoot, uri)
            # print("path: ", path)
            # print("file_extension: ", file_extention)

            if os.path.isfile(path):
                """if file exits, return 200 OK"""
                if os.access(path, os.R_OK):
                    return (path, file_extention, 200)
                else:
                    return (path, file_extention, 403)
            else:
                """ file does not exit, return 404"""
                return (path, file_extention, 404)

        if method == "POST":
            # print("resolve uri post. uri:{}".format(uri))
            if uri == "/data":
                # path = "src/data/data_file1.json"
                path = os.path.join(documnetRoot, "data", "data_file1.json")
                file_extention = "json"
                if os.access(path, os.W_OK):
                    return (path, file_extention, 200)
                else:
                    return (path, file_extention, 403)
            uri = uri.strip('/')
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
            # print("doctumetRoot:{}".format(documnetRoot))
            path = os.path.join(documnetRoot, uri)
            # print("path:", path)
            # print("path calculated:{}".format(path))
            if os.access(path=path, mode=os.F_OK):
                if os.access(path, os.W_OK):
                    return (path, file_extention, 200)
                else:
                    return (path, file_extention, 403)
            else:
                return (path, file_extention, 200)

        if method == "PUT":
            uri = uri.strip('/')
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
            path = os.path.join(documnetRoot, uri)

            """" Check For Existance of file"""
            if os.access(path=path, mode=os.F_OK):
                if os.access(path=path, mode=os.W_OK):
                    """"If write access"""
                    return (path, file_extention, 200)
                else:
                    return (path, file_extention, 403)
            else:
                return (path, file_extention, 200)

        if method == "DELETE":
            uri = uri.strip('/')
            try:
                file_extention = uri.split('.')[1]
            except:
                file_extention = None
            path = os.path.join(documnetRoot, uri)
            if os.path.isdir(uri):
                return(path, file_extention, 403)

            global admin_username, admin_password
            if self.req_headers_general['Authorization']:
                auth = self.req_headers_general['Authorization'].split(" ")[
                    1].encode()
                auth = base64.decodebytes(
                    auth).decode().split(':')
                # print("auth: ", auth)
                username = str(auth[0])
                password = str(auth[1])
                # print(admin_username, admin_password)
                # print("username, password")
                # print(username, password)
            else:
                # print("Authorisation required")
                return (path, file_extention, 401)

            if os.path.isfile(path):
                if os.access(path=path, mode=os.W_OK):
                    # print(admin_username, admin_password, username, password)
                    if (str(username) == str(admin_username) and str(password) == str(admin_password)):
                        # print("Authorized")
                        return (path, file_extention, 200)
                    else:
                        # print("Not Authorized")
                        return (path, file_extention, 401)
                else:
                    return(path, file_extention, 403)
            else:
                return(path, file_extention, 404)

    def create_response(self):
        # Defining response headers (which will always be sent)
        self.res_headers["Date"] = strftime("%a, %d %b %Y %H:%M:%S GMT",
                                            gmtime())
        self.res_headers["Server"] = "localhost"

        if not self.req_headers_general['Cookie']:
            self.cookies = {
                "Name": "Sarvesh",
                "MIS": 1118031489
            }
        if self.res_headers['Status'] == 400:
            response = "{} {} {}\r\n".format("HTTP/1.1", 400,
                                             STATUS_CODES[400])  # Status line
            response = self.add_res_headers(response)
            response += "\r\n400 Bad Request"
            # self.print_res_headers(response)
            return response.encode()

        method, URI, http_version = self.req_headers_general[
            'method'], self.req_headers_general[
                'uri'], self.req_headers_general["protocol"]

        if not http_version == "HTTP/1.1":
            response = "{} {} {}\r\n".format(
                str(http_version), 505, STATUS_CODES[505])  # Status line
            response = self.add_res_headers(response)
            response += "\r\HTTP Version Must Be 1.1"
            return response.encode()

        # status_code is None at this moment unless it is 400
        status_code = self.res_headers['Status']

        # Check if the request format is valid. If valid Move Further
        # Else return 400 response

        # file_path, file_extention, status_code = self.resolve_uri(URI)
        # reason_phrase = STATUS_CODES[status_code]
        # self.res_headers["content-encoding"] = "br"

        if method in ["GET", "HEAD"]:
            file_path, file_extention, status_code = self.resolve_uri(URI)
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             STATUS_CODES[status_code])  # Status line
            print("filepath: {} extension: {} Status Code: {}\n".format(
                file_path, file_extention, status_code))
            self.res_headers['Status'] = status_code
            # if request is valid but status code != 200
            # i.e  404 Not Found, 403 Forbidden
            if status_code != 200:
                response = self.add_res_headers(response)
                # self.print_res_headers(response)
                if status_code == 404:
                    if method == "GET":
                        response += "\r\n" + "404 Page Not Found\r\n"
                    return response.encode()
                elif status_code == 403:
                    if method == "GET":
                        response += "\r\n" + "403 Forbidden\r\n"
                    return response.encode()
                else:
                    if method == "GET":
                        response += "\r\n" + "Not 200 Not Okay\r\n"
                    return response.encode()

            if file_extention in ["ico", "jpeg", "jpg", "pdf", "mp4"]:
                """ get_data() function returns tuple (last-modified date,file_data)"""
                self.res_headers['Last-Modified'], self.res_body = get_data(
                    file_path, file_extention, self.queries)

                if self.res_headers['Last-Modified'] == self.req_headers_general['If-Modified-Since']:
                    # print("not modified image")
                    status_code = 304
                    self.res_headers['Status'] = status_code
                    response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                     STATUS_CODES[status_code])  # Status line
                    response = self.add_res_headers(response)
                    response += "\r\n"
                    # self.print_res_headers(response)
                    return response.encode()

                # print(" modified image")
                # self.res_headers["Content-Length"] = len(self.res_body)
                self.res_headers["Content-Length"] = os.path.getsize(file_path)
                self.res_headers["Accept-ranges"] = "bytes"
                # self.res_headers["Content-type"] = CONTENT_TYPE[file_extention]
                self.res_headers["Content-type"] = mimetypes.guess_type(
                    url=file_path)[0]

                response = self.add_res_headers(response)
                response.strip()
                # self.print_res_headers(response)
                response += "\r\n"

                # encode headers (text); do not encode image_raw as it is binary
                response = response.encode()
                # self.res_body = image_raw
                # response += image_raw

                if method == "GET":
                    response += self.res_body
                ###
                return response

            elif file_extention in ["html", "json", "js"]:
                # print("file extension is: " + str(file_extention))

                self.res_headers['Last-Modified'], self.res_body = get_data(
                    file_path=file_path, file_extension=file_extention, queries=self.queries)
                # print("self.res_body: ", self.res_body)
                if self.res_headers['Last-Modified'] and self.res_headers['Last-Modified'] == self.req_headers_general['If-Modified-Since']:
                    status_code = 304
                    self.res_headers['Status'] = status_code
                    response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                     STATUS_CODES[status_code])  # Status line
                    response = self.add_res_headers(response)
                    response += "\r\n"
                    # self.print_res_headers(response)
                    return response.encode()
                ###

                if self.res_body:
                    # self.res_headers["Content-type"] = CONTENT_TYPE[file_extention]
                    self.res_headers["Content-type"] = mimetypes.guess_type(
                        url=file_path)[0]
                    self.res_headers["Content-Length"] = os.path.getsize(
                        file_path)

                # print("Adding headers by add_res_headers")
                response = self.add_res_headers(response)
                # self.print_res_headers(response)
                if method == "GET":
                    if self.res_body:
                        response += "\r\n" + self.res_body
                elif method == "HEAD":
                    response += "\r\n"
                # self.print_res_headers(response)
                response = response.encode()
                # encode whole response(headers+body) as everything is textual
                return response

            # if file extension is not recognizable. Return Bad Request
            elif file_extention:
                response = "{} {} {}\r\n".format(str(http_version), 400,
                                                 STATUS_CODES[400])  # Status line
                if method == "GET":
                    response += "\r\nExtenstion Of File not recognizable. So Bad Request 400\r\n"
                # self.print_res_headers(response)
                return response.encode()

        # method other than GET
        elif method == "POST":
            # print(
            #     "****************************  Request Headers: Start  ********************")
            # print(self.headers['Content-Length'])
            # print(self.req_headers_general['Content-Length'])
            # print(
            #     "************************   Request Headers: end   ********************\n")
            # print("in Create_response(): method: POST")
            file_path, file_extention, status_code = self.resolve_uri(URI)

            print("Total Content length:{}".format(
                self.req_headers_general['Content-Length']))
            self.total_content_length = self.req_headers_general['Content-Length']
            print("Current Content length: {}".format(
                self.current_content_length))
            self.cumulative_content_length += self.current_content_length
            print("Cumulative Content length: {}".format(
                self.cumulative_content_length))
            while(int(self.cumulative_content_length) < int(self.total_content_length)):
                nextmsg = self.client_socket.recv(4096).decode("iso-8859-1")
                nextmsg_body = nextmsg
                self.current_content_length = len(nextmsg_body)
                self.cumulative_content_length += self.current_content_length
                print("{}\t{}\t{}".format(self.total_content_length,
                                          self.current_content_length, self.cumulative_content_length))
                self.msg_body += nextmsg_body

            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             STATUS_CODES[status_code])  # Status line
            self.res_headers['Status'] = status_code

            if status_code in [403]:
                # print("resolve uri returned 403")
                response += "\r\n Forbidden"
                # self.print_res_headers(response)
                return response.encode()

            print("calling post_data()")
            status_code = post_data(uri=file_path, msg_body=self.msg_body,
                                    file_extension=file_extention, content_type=self.req_headers_general["Content-Type"])
            print("out of post_data()")

            if status_code in [400, 403, 500]:
                response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                 STATUS_CODES[status_code])  # Status line
                self.res_headers['Status'] = status_code
                response = self.add_res_headers(response)
                if status_code == 400:
                    response += "\r\n Bad Request Format"
                elif status_code == 403:
                    response += "\r\n Forbidden"
                elif status_code == 500:
                    response += "\r\n Server Error"

                # self.print_res_headers(response)
                return response.encode()
            if status_code in [200]:
                response = self.add_res_headers(response)
                # self.print_res_headers(response)
                response += "\r\n" + "POST Successful"
                return response.encode()

        elif method == "PUT":
            file_path, file_extention, status_code = self.resolve_uri(URI)
            print("Total Content length:{}".format(
                self.req_headers_general['Content-Length']))
            self.total_content_length = self.req_headers_general['Content-Length']
            print("Current Content length: {}".format(
                self.current_content_length))
            self.cumulative_content_length += self.current_content_length
            print("Cumulative Content length: {}".format(
                self.cumulative_content_length))

            print("Total\tCurrent\tCumulative")
            while(int(self.cumulative_content_length) < int(self.total_content_length)):
                nextmsg = self.client_socket.recv(4096).decode("iso-8859-1")
                nextmsg_body = nextmsg
                self.current_content_length = len(nextmsg_body)
                self.cumulative_content_length += self.current_content_length
                print("{}\t{}\t{}".format(self.total_content_length,
                                          self.current_content_length, self.cumulative_content_length))
                self.msg_body += nextmsg_body

            print("Calling manage_data.put_data")
            status_code, resource_uri = manage_data.put_data(uri=file_path, msg_body=self.msg_body, file_extension=file_extention,
                                                             content_type=self.req_headers_general["Content-Type"])
            print("Out of manage_data.put_data")

            if status_code in [400, 404]:
                response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                 STATUS_CODES[status_code])  # Status line

                if status_code == 404:
                    self.res_body = "\r\nDirectory Does not exist"
                elif status_code == 400:
                    self.res_body = "\r\nBad Request"
                self.res_headers['Status'] = status_code
                self.res_headers["Content-Length"] = len(self.res_body)
                response = self.add_res_headers(response)
                response += self.res_body
                # self.print_res_headers(response)
                return response.encode()

            # print("method : PUT: ", file_path, file_extention, status_code)
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             STATUS_CODES[status_code])  # Status line

            if status_code == 200:
                self.res_body = "PUT OKAY"
            elif status_code == 201:
                self.res_body = "File Created"
                self.res_headers['Location'] = os.path.relpath(
                    path=resource_uri, start=documnetRoot)

            self.res_headers['Status'] = status_code
            self.res_headers["Content-Length"] = len(self.res_body)
            response = self.add_res_headers(response)
            response += "\r\n" + self.res_body
            # self.print_res_headers(response)
            return response.encode()

        elif method == "DELETE":
            file_path, file_extention, status_code = self.resolve_uri(URI)
            # print("method : DELETE: ", file_path, file_extention, status_code)

            if status_code != 200:
                response = "{} {} {}\r\n".format(str(http_version), status_code,
                                                 STATUS_CODES[status_code])  # Status line
                self.res_body = STATUS_CODES[status_code]
                # self.res_headers["Content-Length"] = len(self.msg_body)
                response = self.add_res_headers(response)
                response += "\r\n"
                # self.print_res_headers(response)
                return response.encode()

            # print("Calling delete_data()")
            status_code = manage_data.delete_data(
                uri=file_path, file_extension=file_extention, queries=self.queries)
            # print("After delete_data(): status_code: ", status_code)

            reason_phrase = STATUS_CODES[status_code]
            self.res_headers['Status'] = status_code
            response = "{} {} {}\r\n".format(str(http_version), status_code,
                                             reason_phrase)  # Status line
            if status_code == 200:
                self.res_body = "File Successfully Removed"
            elif status_code == 403:
                self.res_body = "Forbidden"
            elif status_code == 400:
                self.res_body = "Do not give query strings for DELETE request for html, jpeg, png, jpg files"
            elif status_code == 500:
                self.res_body = "Internal Server Error"

            self.res_headers["Content-Length"] = len(self.msg_body)
            response = self.add_res_headers(response)
            response += "\r\n" + self.res_body
            # print("Response : ")
            # self.print_res_headers(response)
            return response.encode()

        else:
            file_path, file_extention, status_code = self.resolve_uri(URI)
            status_code = 400
            self.res_headers['Status'] = status_code
            reason_phrase = STATUS_CODES[status_code]
            response = "{} {} {}".format(str(http_version), 400, reason_phrase)
            response = self.add_res_headers(response)
            response += "\r\n"
            # self.print_res_headers(response)
            return response.encode()


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

    def stop_server(self):
        self.server_socket.close()

    def close_server(self):
        self.server_socket.close()


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
        global max_thread_count
        if max_thread_count < threading.activeCount():
            max_thread_count = threading.activeCount()

        # print("Active Threads:{} Current Client Thread:{} max_thread_count:{}\n".format(
        #     threading.activeCount(), threading.currentThread(), max_thread_count))
        """ iso-8859-1 decoding to decode image(binary files without any issues) """
        msg = self.client_socket.recv(4096).decode("iso-8859-1")
        """
            If msg is None... For now sendd 400
        # """
        print("****************************  Request msg: Start  ********************")
        print(msg)
        print("*****************************   Request msg: end   ********************\n")

        try:
            self.extract_msg(msg)
            self.extract_headers()
        except:
            self.client_socket.close()
            request_line = None
            log.error_log(status_code=500, size=len("Server Error"), request_line=request_line,
                          client_ip=self.ip, user_agent=self.req_headers_general['User-Agent'], logDir=logDir)
            return

        if self.res_headers['Status'] == 400:
            self.process_query()
            self.client_socket.close()
            return
        # print("****************************  Request Headers: Start  ********************")
        # print(self.headers)
        # print("************************   Request Headers: end   ********************\n")

        request_line = self.req_headers_general['method'] + " " + \
            self.req_headers_general['uri'] + " " + \
            self.req_headers_general['protocol']
        try:
            self.process_query()
            self.client_socket.close()
            log.access_log(status_code=self.res_headers["Status"], size=self.res_headers["Content-Length"], request_line=request_line,
                           client_ip=self.ip, user_agent=self.req_headers_general['User-Agent'], logDir=logDir)
        except:
            self.client_socket.close()
            log.error_log(status_code=500, size=len("Server Error"), request_line=request_line,
                          client_ip=self.ip, user_agent=self.req_headers_general['User-Agent'], logDir=logDir)
            return
        # print_linebreak()

    def process_query(self):
        response = self.create_response()
        self.client_socket.send(response)
        return


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    os.system(
        command="kill $( ps aux | grep 'python3 server.py' | awk '{print $2}')")
    print("Server Stopped")
    sys.exit(0)


def listen_for_interrupt():
    while True:
        signal.signal(signal.SIGINT, signal_handler)
    signal.pause()


def listen_for_input(server):
    global SEREVR_STATE
    while True:
        inp = input()
        if inp in ["STOP", "Stop", "stop"]:
            print("Server Stopped")
            server.close_server()
            os.system(
                command="kill $( ps aux | grep 'server.py' | awk '{print $2}')")
        elif inp in ["Pause", "PAUSE", "pause"]:
            SEREVR_STATE = "PAUSED"
            print('Server Paused.. Enter "Restart" to start the server')
        elif inp in ["restart", "Restart", "RESTART"]:
            if SEREVR_STATE == "PAUSED":
                print("Server Restarted")
                SEREVR_STATE = "RUNNING"
            else:
                print("Invalid input")
        else:
            print("Invalid input")


if __name__ == "__main__":
    # global SEREVR_STATE

    signal.signal(signal.SIGINT, signal_handler)
    port = PORT
    http_server = Server('', port)
    http_server.start_server()
    threading.Thread(target=listen_for_input, args=(http_server,)).start()
    # print_linebreak()
    # print("Main Threads:{}\tCurrent Main Thread:{}\n".format(
    # threading.activeCount(), threading.currentThread()))
    while True:
        if SEREVR_STATE != "PAUSED":
            (client_socket, (ip, port)) = http_server.server_socket.accept()
            newClientThread = ClientThread(ip, port, client_socket)
            newClientThread.start()

    for t in threads:
        t.join()
