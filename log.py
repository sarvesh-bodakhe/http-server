# class Log:
#     def __init__(self, client_addr):
#         self.access_log_file = "log/access.log"
#         self.client_addr = client_addr

#     # def access_log(self, status_code, size, request)

import time


def access_log(status_code, size, request_line, client_ip, user_agent):
    if not size:
        size = 0

    # print("in access_log")
    log = str(client_ip) + " - - "
    log += get_time() + " "
    log += '"' + request_line + '" '
    log += str(status_code) + " "
    log += str(size) + ' "-" '
    log += '"' + str(user_agent) + '"' + "\n"

    # print("in access_log log to be printed: ", log)
    file_obj = open("log/access.log", "a")
    file_obj.write(log)
    file_obj.close()


def get_time():
    localtime = time.asctime(time.localtime(time.time()))
    localtime = localtime.split(" ")
    return "[" + (localtime[2]) + "/" + localtime[1] + "/" + \
        localtime[4] + ":" + str(localtime[3]) + " +0530" + "]"


# print("In Log")
# print(get_time())
