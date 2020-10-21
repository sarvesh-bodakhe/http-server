import os
from pathlib import Path


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


# print(resolve_uri("/image_server_012.jpeg"))
uri = "/moodle/course/view.php?id=10&name=Sarvesh"
try:
    a, b = uri.split('?')
    b = b.split('&')
except:
    a = uri
    b = None
print("a: ", a)
print("b: ", b)
# print(uri.split('?'))
