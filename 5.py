from configparser import ConfigParser
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import os
import sys
import threading
import mimetypes
values = [2, 3, 4, 5]


def square(n):
    print("Count Threads:{}\tCurrent Thread:{}\n".format(
        threading.activeCount(), threading.currentThread()))
    return n * n


def main():
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix='client_thread') as executor:
        results = executor.map(square, values)
    for result in results:
        print(result)


# config = ConfigParser()
# config.read('config.ini')
# print(config.sections())
# print(config['SERVER']['port'])

# if os.access("src/data/data_file1.json", os.F_OK):
#     print("Access Granted")
# else:
#     print("Access Denied")

# print(mimetypes.guess_type(url="src/data/data_file1.json"))
# print(mimetypes.guess_type(url="src/data/postedFiles/images (2).jpg"))
# print(mimetypes.guess_type(url="src/data/postedFiles/temp.png"))

# path = "temp.txt"
# fp = open(path)
# fp = fp.read()
# print(sys.getsizeof(fp))
# print(os.path.getsize(path))

# path1 = "/home/luffy/sem5/subj/cn/project/http2/src"
# path2 = "/home/luffy/sem5/subj/cn/project/http2/src/data/data_file1.json"
# print(os.path.relpath(path=path2, start=path1))

if os.access("home/luffy/sem5/subj/cn/project/http2/src/data/data_file1.json", os.F_OK):
    print("Access Granted")
else:
    print("Access Denied")
