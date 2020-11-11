# class Log:
#     def __init__(self, client_addr):
#         self.access_log_file = "log/access.log"
#         self.client_addr = client_addr

#     # def access_log(self, status_code, size, request)
import time
import os


def access_log(status_code, size, request_line, client_ip, user_agent, logDir=None):
    if not size:
        size = 0

    # print("in access_log, LogDir: ", logDir)
    log = str(client_ip) + " - - "
    log += get_time() + " "
    log += '"' + request_line + '" '
    log += str(status_code) + " "
    log += str(size) + ' "-" '
    log += '"' + str(user_agent) + '"' + "\n"

    # print("in access_log log to be printed: ", log)
    file_path = os.path.join(logDir, "access.log")
    file_obj = open(file_path, "a")
    file_obj.write(log)
    file_obj.close()


def get_time():
    localtime = time.asctime(time.localtime(time.time()))
    # print(localtime)
    localtime = localtime.split()
    # print(localtime)
    return "[" + (localtime[2]) + "/" + localtime[1] + "/" + \
        localtime[4] + ":" + str(localtime[3]) + " +0530" + "]"


# print("In Log")
# print(get_time())
