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


def send_request_fun(request):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(request.encode())
    response = client_socket.recv(10000000).decode()
    # print("response received: length:{}".format(len(response)))
    client_socket.close()
    global req_no
    req_no += 1
    print("Request No:{} Response Length:{}".format(req_no, len(response)))
    return len(response)


if __name__ == "__main__":
    file_obj = open("requests.json", "r")
    obj_list = json.load(file_obj)
    print("requests count: {}".format(len(obj_list)))
    main_list = []
    for i in obj_list:
        temp = i['body']
        main_list.append(temp)

    print("requests count: {}".format(len(main_list)))
    start_time = time.time()

    start_time = time.time()
    num = int(input("Enter how many requests to send: "))
    req_list = main_list[:num]
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
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
                # print("{}: {}".format(req_no, data)
                pass

    end_time = time.time()
    print("Time required: {} sec".format(end_time-start_time))
