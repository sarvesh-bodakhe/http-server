import os
import time
from pathlib import Path
from time import gmtime, strftime


def resolve_uri(uri):
    print("initial URI: " + uri)

    if uri == "/":
        print("Path exits")
        path = "src/index.html"
        file_extention = "html"
        return (path, 200)

    path = "src"
    uri = uri.strip('/')
    file_extention = uri.split('.')[1]
    # print("filename: ", uri)
    path = os.path.join(path, uri)
    print("Path: ", path)
    print("file_extention: ", file_extention)
    if os.path.isfile(path):
        print("file exits")
        return (path, 200)
    else:
        print("file does not exit")
        return (path, 404)


# # print(resolve_uri("/image_server_012.jpeg"))
# uri = "/moodle/course/view.php?id=10&name=Sarvesh"
# try:
#     a, b = uri.split('?')
#     b = b.split('&')
# except:
#     a = uri
#     b = None
# print("a: ", a)
# print("b: ", b)
# print(uri.split('?'))
print("Create :  {}".format(time.ctime(os.path.getctime("server.py"))))
print("Last Modified: {}".format(time.ctime(os.path.getmtime("server.py"))))
print(strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()))
print(time.ctime(os.path.getmtime("server.py")))

# print(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"))

# print(time.ctime(os.path.getctime("server.py")))
# print(time.ctime(os.path.getmtime("server.py")))
print(os.path.getctime("server.py"))


def get_modification_time(file_name):
    return strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(os.path.getmtime(file_name)))


print("fun: ")
print(get_modification_time("server.py"))
