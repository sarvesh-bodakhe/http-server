import sys
from socket import *
from time import gmtime, strftime
import json
import threading
import concurrent
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import time

import os
from multiprocessing import Process
import multiprocessing

host = '127.0.0.1'
port = int(sys.argv[1])
req_no = 0


def send_request_fun(request):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(request.encode())
    response = client_socket.recv(10000000).decode()
    # print("response received: length:{}".format(len(response)))
    client_socket.close()
    global req_no
    req_no += 1
    process_id = os.getpid()
    # print("{}: {} pid:{}".format(req_no, len(response), process_id))
    # return len(response)


if __name__ == "__main__":
    file_obj = open("requests.json", "r")
    obj_list = json.load(file_obj)
    print("requests count: {}".format(len(obj_list)))
    req_list = []
    for i in obj_list:
        temp = i['body']
        req_list.append(temp)

    processes = []

    for request in req_list:
        process = Process(target=send_request_fun, args=(request,))
        processes.append(process)
        process.start()

        #

    print("requests count: {}".format(len(req_list)))
    # print(req_list[0])
