from socket import *
import threading
import sys
import requests
import mimetypes
import base64
import json

count = 0
if_modified_since_time = 0
if_unmodified_since_time = 0
port = 2000

file_obj = open("requests_testing.json", "r")
req_list = json.load(file_obj)


def send_request(request, description=None):
    print("Request Description: ", description)
    print()
    print("Request Headers: ")
    try:
        req_header, req_body = request.split('\r\n\r\n', 1)
    except:
        req_header = request.split("\r\n\r\n")
        req_body = None
    print(req_header)
    print()
    if req_body:
        print("Request Body")
        print(req_body)
        print()

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(request.encode())
    response = client_socket.recv(10000000).decode('iso-8859-1')
    client_socket.close()
    try:
        res_headers, res_body = response.split("\r\n\r\n", 1)
    except:
        res_headers = response.strip("\r\n")
        res_body = None
    print("Response Headers:")
    res_headers = res_headers.split("\r\n")
    for line in res_headers:
        print(line)
    print()
    print("Response Body:")
    if not res_body:
        print(res_body)
    elif res_body and (len(res_body) < 1000) and len(res_body) > 0:
        print(res_body)
    elif len(res_body) >= 1000:
        print("Response Body is too big to print")

    global count
    count += 1
    # print("{}: {}".format(count, len(response)))
    print("-" * 100)
    return


def solve(num):
    if num == 1:
        for request in req_list:
            if request['method'] == "GET":
                send_request(request['body'],
                             description=request['description'])
        print()
        print()
        return
    if num == 2:
        for request in req_list:
            if request['method'] == "HEAD":
                send_request(request['body'],
                             description=request['description'])
        print()
        print()
        return

    if num == 3:
        for request in req_list:
            if request['method'] == "POST":
                send_request(request['body'],
                             description=request['description'])
        print()
        print()
        return
    if num == 4:
        PUT_request()

    if num == 5:
        for request in req_list:
            if request['method'] == "DELETE":
                send_request(request['body'],
                             description=request['description'])
        print()
        print()
    else:
        print("Please select a valid number")


def PUT_request():
    fname = "temp.txt"
    with open(fname, 'rb') as f:
        content_type = mimetypes.guess_type(fname)[0]
        # print(content_type)
        data = f.read()
    response = requests.put('http://localhost:' + str(port) + '/' +
                            'data/putFiles', data=data, headers={'Content-Type': content_type})
    response.encoding = 'utf-8'
    status = response.status_code
    print("Request: POST /data/putFiles HTTP/1.1")
    print(status)
    print()
    headers = response.headers
    print("Response Headers")
    print_headers(headers)
    print()
    body = response.content
    print("Response Body")
    print(body)
    print("-"*100)


def print_headers(headers):
    for attribute in headers:
        print("{}: {}".format(attribute, headers[attribute]))
    print()


if __name__ == "__main__":

    host = '127.0.0.1'
    port = 8800
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    inp = int(input("Enter which request to TEST:\nGET: 1\tHEAD: 2\tPOST: 3\tPUT: 4\tDELETE: 5\tTo quit testing: 0\nEnter the Number: "))
    while inp != 0:
        solve(inp)
        inp = int(input(
            "Enter which request to TEST:\nGET: 1\tHEAD: 2\tPOST: 3\tPUT: 4\tDELETE: 5\tTo quit testing: 0\nEnter the Number: "))
