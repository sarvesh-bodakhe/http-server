import sys
from socket import *
from time import gmtime, strftime
import json
import threading
import concurrent
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import time

host = '127.0.0.1'
port = int(sys.argv[1])

"""
    Use concurrent library to make simultaneous requets
"""

req_no = 0


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
        self.request_uri = "/data"
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
        # print("************** self.request: start *************")
        # print(self.request)
        # print("**************** self.request: end **************")

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
        # print("****************** Sending request: end ******************")
        self.listen()


class client_thread():
    def __init__(self, request):
        self.request = request
        self.port = port
        self.client_thread_socket = socket(AF_INET, SOCK_STREAM)
        self.client_thread_socket.connect((host, port))

    def listen(self):
        response = self.client_thread_socket.recv(100000000).decode()
        print("Received msg by server: start")
        print(response)
        # print("Received msg by server: end")
        self.client_thread_socket.close()

    def send_request(self):
        # self.client_thread_socket = socket(AF_INET, SOCK_STREAM)
        # self.client_thread_socket.connect((host, port))
        print("****************** Sending request: start ******************")
        self.client_thread_socket.send(self.request.encode())
        # print("****************** Sending request: end ******************")
        self.listen()


def send_request_fun(request):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(request.encode())
    response = client_socket.recv(10000000).decode()
    # print("response received: length:{}".format(len(response)))
    client_socket.close()
    global req_no
    req_no += 1
    # print("{}: {}".format(req_no, len(response)))
    return len(response)


if __name__ == "__main__":
    # print("In main")
    # c = client()
    # c.create_request()
    # c.create_request()
    # c.send_request()
    # c.listen()

    """
        Code to write request into json file
    """
    # file_obj = open("requests.json", "r")
    # obj_list = json.load(file_obj)
    # temp_dict = dict()
    # temp_dict['body'] = c.request
    # json_obj = json.dumps(temp_dict)
    # json_obj = json.loads(json_obj)
    # obj_list.append(json_obj)
    # fp = open("requests.json", "w")
    # json.dump(obj_list, fp)
    # print("request count in file: {}".format(len(obj_list)))
    """
        Code to send requests from request.txt file
    """

    # file_obj = open("requests.json", "r")
    # obj_list = json.load(file_obj)
    # for request in obj_list:
    # print("****************************")
    # print(request)
    # print("****************************")
    # c = client_thread(request['body'])
    # c.send_request()

    # c = client_thread("hi")

    """
        Code for threadpull
    """
    file_obj = open("requests.json", "r")
    obj_list = json.load(file_obj)
    print("requests count: {}".format(len(obj_list)))
    req_list = []
    for i in obj_list:
        temp = i['body']
        req_list.append(temp)

    print("requests count: {}".format(len(req_list)))
    start_time = time.time()
    # with ThreadPoolExecutor(max_workers=1000, thread_name_prefix='client_thread') as executor:
    #     results = executor.map(send_request_fun, req_list)
    # # for result in results:
    # #     print(result)

    # global req_no
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(
            send_request_fun, req): req for req in req_list}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result(timeout=1)
            except concurrent.futures.TimeoutError:
                print("{} maybe took long generated an exception".format(req_no))
            else:
                print("{}: {}".format(req_no, data))

    end_time = time.time()
    print("Time required: {}".format(end_time-start_time))

    """
        req_count   max_workers     time(s)    max_threads
        736         1000
        736         200             124         16
        736         30              124         12
        736         20              1.85        9
        736         10              1.75        7
        736         5               1.053       7
        736         1               0.24        2
    """
