import csv
import json
import os
import time
from time import gmtime, strftime


def display_file():
    fp = open("src/data/data_file1.json", "r")
    data = json.load(fp)
    print(data)


def delete_data(uri, file_extension=None, queries=None):
    print("In delete_data")
    print("uri: ", uri, " Query: ", queries, " extension: ", file_extension)

    if os.path.exists(uri):
        print("file exits")
        if file_extension == "json":
            if len(queries) == 0:
                """  Delete Complete file  """
                try:
                    os.remove(uri)
                    print("File successfully removed")
                    return 200
                except:
                    print("Failed to delete file")
                    return 500

            else:
                """ Delete data matching queries """
                file_obj = open(uri, "r")
                obj_list = json.load(file_obj)
                file_obj.close()
                for obj in obj_list:
                    print("obj: ", obj)
                    for attr in queries:
                        # print("attr: ", attr, "Value: ", queries[attr])
                        # print("obj[attr]: ", obj[attr])
                        if str(obj[attr]) == str(queries[attr]):
                            print("found")
                            obj_list.remove(obj)
                            break
                print("SuccessFully removed")
                file_obj = open(uri, "w")
                json.dump(obj_list, file_obj)
                file_obj.close()
                return 200

        elif file_extension in ["html", "jpeg", "png", "jpg", "txt"]:
            if len(queries) == 0:
                """
                    Delete file here
                """
                try:
                    os.remove(uri)
                    print("File successfulyy removed")
                    return 200
                except:
                    return 500
            else:
                """
                    there should not be any queries with these extensions
                """
                print(
                    "Do not give query strings for DELETE request for html, peg, png, jpg files")
                return 400

    else:
        print("File does not exits")
        return 404


"""
        The PUT method requests that the enclosed entity be stored under the
        supplied Request-URI.
                If the Request-URI refers to an already
                existing resource, the enclosed entity SHOULD be considered as a
                modified version of the one residing on the origin server. If the
                Request-URI does not point to an existing resource, and that URI is
                capable of being defined as a new resource by the requesting user
                agent, the origin server can create the resource with that URI. If a
                new resource is created, the origin server MUST inform the user agent
                via the 201 (Created) response. If an existing resource is modified,
                either the 200 (OK) or 204 (No Content) response codes SHOULD be sent
                to indicate successful completion of the request.
"""

# Currently no check for directory


def put_data(uri, msg_body, file_extension, content_type):
    print("in put_data : uri: ", uri, " msg_body: ",
          msg_body, " file_extension: ", file_extension, " Content-type: ", content_type)
    uri = uri.strip('/')

    if os.path.exists(uri):
        """
            File exits. Open it and put request_body as file contents
        """
        print("File exits")
        file_obj = open(uri, "w")
        file_obj.write(msg_body)
        file_obj.close()
        return 200
    else:
        """
            File Does not exit. Create it and put request_body as file contents
        """
        print("File does not exit")
        file_obj = open(uri, "w")
        file_obj.write(msg_body)
        file_obj.close()
        return 201


def post_data(uri, msg_body, file_extension, content_type):
    print("in post_data : uri: ", uri,  " file_extension: ",
          file_extension, " Content-type: ", content_type)
    print("msg_body: ")
    print(msg_body)
    uri = uri.strip('/')
    if os.path.exists(uri):
        print("File exits")
    else:
        print("File does not exits. Creating file...")

    if content_type == "application/x-www-form-urlencoded":

        msg_body = msg_body.split('&')
        print("msg_body: ", msg_body)
        temp_dict = dict()
        for i in msg_body:
            try:
                temp = i.split('=')
                key = temp[0]
                value = temp[1]
                temp_dict[key] = value
            except:
                """  Wrong format   """
                return 400

        # temp_dict['filename'] = None
        # temp_dict['fileuri'] = None
        print("temp_dict: ", temp_dict)
        json_obj = json.dumps(temp_dict)
        json_obj = json.loads(json_obj)
        json_obj['Year'] = int(json_obj['Year'])
        json_obj['MIS'] = int(json_obj['MIS'])

        print("json_obj: ", json_obj)

        if os.path.exists(uri):
            fp = open(uri, "r")
            obj = json.load(fp)
        else:
            obj = []

        obj.append(json_obj)
        fp = open(uri, "w")
        json.dump(obj, fp)
        return 200

    elif content_type.find("multipart/form-data") != -1:
        """

        """
        print("content type is multipart/form-data")

        """
            Do not know why boundary calculated is short of "--"
        """
        try:
            # print("Viraj requested: ", content_type.split(';')[1])
            # print("Vireaj reques ended")
            boundary = "--" + content_type.split(';')[1].split('=')[1]
            print("Boundary calculated: ", boundary)
        except:
            return 400

        temp_dict = dict()
        temp_msg = msg_body.strip(boundary).split(boundary)
        print("temp_split: ")
        temp_msg = temp_msg[:-1]
        print(temp_msg)

        # print("split by boundary :", temp_msg)
        for line in temp_msg:
            # print("line: ", line)
            info_dict = dict()
            info_dict['filename'] = None
            info_dict['Content-Type'] = None
            temp = line.strip('\r\n')

            """
                if file is empty. error will occur here
            """
            try:
                info, value = temp.split('\r\n\r\n')
            except:
                continue
            # print(temp, value)
            info = info.split(';')

            info_dict['Content-Disposition'] = info[0].split(':')[1].strip()
            info_dict['name'] = info[1].split('=')[1].strip('"')
            try:
                info_dict['filename'] = info[2].split(
                    '\r\n')[0].split('=')[1].strip('"')
                info_dict['Content-Type'] = info[2].split(
                    '\r\n')[1].split(':')[1].strip()
                file_path = os.path.join(
                    "src/data/postedFiles", info_dict['filename'])

                print("file to create + uri: ", file_path)
                file_obj = open(file_path, "w")
                file_obj.write(value)
                file_obj.close()
            except:
                print("Unable to create file")
                pass

            info_dict['value'] = value
            print("Info_dict: ")
            print(info_dict)

            if info_dict['filename']:
                print("File included")
            try:
                temp_dict[info_dict['name']] = info_dict['value']
            except:
                return 400
            print()

        temp_dict['filename'] = info_dict['filename']
        temp_dict['fileuri'] = None
        print("Object to append: ", temp_dict)
        json_obj = json.dumps(temp_dict)
        json_obj = json.loads(json_obj)
        json_obj['Year'] = int(json_obj['Year'])
        json_obj['MIS'] = int(json_obj['MIS'])

        print("json_obj: ", json_obj)

        if os.path.exists(uri):
            # print("File exits")
            fp = open(uri, "r")
            obj = json.load(fp)
        else:
            # print("File does not exist")
            obj = []

        obj.append(json_obj)
        # print("List to append: ", obj)
        try:
            fp = open(uri, "w")
            json.dump(obj, fp)
            return 200
        except:
            print("Unable to open file")
            return 500

    return 400


def get_modification_time(file_name):
    return strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(os.path.getmtime(file_name)))


def get_data(file_path, file_extension=None, queries=None):
    print("in get_data()-> file_path:", file_path, " file_extension:",
          file_extension, "queries:", queries)

    if file_extension in ["ico", "jpeg", "jpg"]:
        file_obj = open(file_path, 'rb')
        image_raw = file_obj.read()
        return (get_modification_time(file_path), image_raw)

    elif file_extension in ["html", "json", "js"]:
        if file_extension == "json" and queries:
            file_obj = open(file_path, "r")
            # obj_list is list of objects (json)
            obj_list = json.load(file_obj)
            to_return = []
            for obj in obj_list:
                print("obj: ", obj)
                for attr in queries:
                    print("attr: ", attr, "Value: ", queries[attr])
                    print("obj[attr]: ", obj[attr])
                    if str(obj[attr]) == str(queries[attr]):
                        print("found")
                        return (None, json.dumps(obj))
            return (None, "No Data Available")

        file_obj = open(file_path, "r")
        text_data = file_obj.read()
        return (get_modification_time(file_path), text_data)


# def set_cookie(keys_values, msg=''):
#     print("in set_cookie: ")
#     print(keys_values)
#     try:
#         for key in keys_values:
#             msg += 'Set-Cookie: {}={}\r\n'.format(key, keys_values[key])
#     except:
#         pass
#     print(msg)


# dict1 = {
#     "Name": "Sarvesh",
#     "Password": 123
# }

# set_cookie(dict1)
# display_file()
