from configparser import ConfigParser
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import threading
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


config = ConfigParser()
config.read('config.ini')
print(config.sections())
print(config['SERVER']['port'])
