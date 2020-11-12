from server import documnetRoot
import csv
import json
import os
import time
from time import gmtime, strftime

put_file_count = 0


dict_extensions = {
    "text/plain": "txt",
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/jpg": "jpg",
}


def display_file():
    fp = open("src/data/data_file1.json", "r")
    data = json.load(fp)
    fp.close()
    print(data)


def delete_data(uri, file_extension=None, queries=None):
    # print("In delete_data")
    # print("uri: ", uri, " Query: ", queries, " extension: ", file_extension)
    uri = os.path.join(documnetRoot, uri)
    # print(uri)
    if os.path.exists(uri):
        # print("file exits")
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
                if os.access(path=uri, mode=os.W_OK):
                    file_obj = open(uri, "r")
                    obj_list = json.load(file_obj)
                    file_obj.close()
                    for obj in obj_list:
                        # print("obj: ", obj)
                        flag = 1
                        for attr in queries:
                            # print("attr: ", attr, "Value: ", queries[attr])
                            # print("obj[attr]: ", obj[attr])
                            if str(obj[attr]) != str(queries[attr]):
                                # print("found")
                                flag = 0
                                # obj_list.remove(obj)
                        if flag == 1:
                            # print("object found")
                            obj_list.remove(obj)

                    # print("SuccessFully removed")
                    file_obj = open(uri, "w")
                    json.dump(obj_list, file_obj)
                    file_obj.close()
                    return 200
                else:
                    print("No write access")
                    return 403

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
    # print("in put_data : uri: ", uri, " file_extension: ",file_extension, " Content-type: ", content_type)
    # uri = uri.strip('/')
    global put_file_count
    if os.path.isdir(uri):

        put_file_count += 1
        file_name = "file_" + str(put_file_count) + \
            "." + dict_extensions[content_type]
        # print("file name create:{}".format(file_name))
        file_path = os.path.join(uri, file_name)

        if content_type in ['text/plain']:
            file_obj = open(file=file_path, mode="w")
            file_obj.write(msg_body)
            file_obj.close()
            return (201, file_path)
        #  content_type in ['image/png', 'image/jpeg', 'image/jpg']:
        else:
            file_obj = open(file=file_path, mode="wb")
            file_obj.write(msg_body.encode('iso-8859-1'))
            file_obj.close()
            return (201, file_path)

    elif os.path.isfile(uri):
        file_path = uri
        file_obj = open(file=file_path, mode="w")
        file_obj.write(msg_body)
        file_obj.close()
        return (200, file_path)
    else:
        # print("else in put_daata")
        return(404, uri)
    # if os.path.exists(uri):
    #     """
    #         File exits. Open it and put request_body as file contents
    #     """
    #     print("File exits")
    #     file_obj = open(uri, "w")
    #     file_obj.write(msg_body)
    #     file_obj.close()
    #     return 200
    # else:
    #     """
    #         File Does not exit. Create it and put request_body as file contents
    #     """
    #     print("File does not exit")
    #     file_obj = open(uri, "w")
    #     file_obj.write(msg_body)
    #     file_obj.close()
    #     return 201


def post_data(uri, msg_body, file_extension, content_type):
    # print("in post_data : uri: ", uri,  " file_extension: ",file_extension, " Content-type: ", content_type)
    # print("msg_body: ")
    # print(msg_body)
    # uri = uri.strip('/')
    # if os.path.exists(uri):
    # print("File exits")
    # else:
    # print("File does not exits. Creating file...")

    if content_type == "application/x-www-form-urlencoded":

        msg_body = msg_body.split('&')
        # print("msg_body: ", msg_body)
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

        # print("temp_dict: ", temp_dict)
        json_obj = json.dumps(temp_dict)
        json_obj = json.loads(json_obj)
        json_obj['Year'] = int(json_obj['Year'])
        json_obj['MIS'] = int(json_obj['MIS'])

        # print("json_obj: ", json_obj)

        if os.path.exists(uri):
            if os.access(path=uri, mode=os.R_OK):
                fp = open(uri, "r")
                obj_list = json.load(fp)
                fp.close()
            else:
                return 403
        else:
            obj_list = []

        obj_list.append(json_obj)

        if os.path.exists(uri):
            if os.access(path=uri, mode=os.W_OK):
                fp = open(uri, "w")
            else:
                return 403
        else:
            fp = open(uri, "w")

        json.dump(obj_list, fp)
        fp.close()
        return 200

    elif content_type.find("multipart/form-data") != -1:
        """

        """
        # print("content type is multipart/form-data")

        """
            Do not know why boundary calculated is short of "--"
        """
        try:
            # print("Viraj requested: ", content_type.split(';')[1])
            # print("Vireaj reques ended")
            boundary = "--" + content_type.split(';')[1].split('=')[1]
            # print("Boundary calculated: ", boundary)
        except:
            return 400

        temp_dict = dict()
        temp_msg = msg_body.strip(boundary).split(boundary)
        # print("temp_split: ")
        """IF image is given, No need to exclude last element"""
        temp_msg = temp_msg[:-1]
        # print(temp_msg)

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
                info, value = temp.split('\r\n\r\n', 1)
            except:
                continue
            # print(info, value)
            info = info.split(';')

            info_dict['Content-Disposition'] = info[0].split(':')[1].strip()
            info_dict['name'] = info[1].split('=')[1].strip('"')
            # print("name: ", info_dict['name'])
            try:
                path_to_postDir = os.path.join(
                    documnetRoot, "data", "postedFiles")
                info_dict['filename'] = info[2].split(
                    '\r\n', 1)[0].split('=')[1].strip('"')
                info_dict['Content-Type'] = info[2].split(
                    '\r\n', 1)[1].split(':')[1].strip()
                file_path = os.path.join(
                    path_to_postDir, info_dict['filename'])
                # file_path = os.path.relpath(path=file_path, start=documnetRoot)
                # temp_dict['filename'] = info_dict['filename']
                temp_dict['fileuri'] = os.path.relpath(
                    path=file_path, start=documnetRoot)
                # print("file to create:", file_path)
                # print("filename:{} content-type:{}".format(info_dict['filename'], info_dict['Content-Type']))

                extenstion_of_file = info_dict['filename'].split('.')[1]
                # if extenstion_of_file in ['jpeg', 'png', 'jpg']:
                if info_dict['Content-Type'] in ["image/jpeg", "image/jpg"] or extenstion_of_file in ['jpeg', 'png', 'jpg']:
                    # print("image is of type jpg, jpeg, png - Binary")

                    if os.access(path=file_path, mode=os.F_OK):
                        if os.access(path=file_path, mode=os.W_OK):
                            # print("file already exits. and have write access")
                            # print("filepath:{}".format(file_path))
                            try:
                                file_obj = open(file_path, "wb")
                                file_obj.write(value.encode('iso-8859-1'))
                                # print("image written in file")
                                file_obj.close()
                            except:
                                # print("internal server error")
                                return 500
                        else:
                            # print("file already exits. but dont have write access. 403")
                            return 403
                    else:
                        # print("file do not exits")
                        # print("filepath:{}".format(file_path))
                        file_obj = open(file_path, "wb")
                        file_obj.write(value.encode('iso-8859-1'))
                        # print("image written in file")
                        file_obj.close()

                    # try:
                    #     file_obj = open(file_path, "wb")
                    #     # print("File opened")
                    #     # value = value.encode('iso-8859-1')
                    #     # print("file-contents:")
                    #     # print("Viraj Value:")
                    #     print(value.encode('iso-8859-1'))
                    #     file_obj.write(value.encode('iso-8859-1'))
                    #     print("image written in file")
                    # # file_obj.write(value)
                    #     # print("File written")
                    #     file_obj.close()
                    #     # print("file written successfully")
                    # except:
                    #     print("Unable to open ", file_path)
                elif extenstion_of_file in ['txt', 'csv', 'js', 'html']:
                    # print("file is of type txt, csv, html, js- Non Binary")
                    if os.access(path=file_path, mode=os.F_OK):
                        if os.access(path=file_path, mode=os.W_OK):
                            # print("file already exits. and have write access")
                            # print("filepath:{}".format(file_path))
                            try:
                                file_obj = open(file_path, "wb")
                                file_obj.write(value.encode('iso-8859-1'))
                                # print("image written in file")
                                file_obj.close()
                            except:
                                # print("internal server error")
                                return 500
                        else:
                            print(
                                "file already exits. but dont have write access. 403")
                            return 403
                    else:
                        # print("file do not exits")
                        # print("filepath:{}".format(file_path))
                        file_obj = open(file_path, "wb")
                        file_obj.write(value.encode('iso-8859-1'))
                        # print("image written in file")
                        file_obj.close()

                    # try:
                    #     file_obj = open(file_path, "w")
                    #     file_obj.write(value)
                    #     file_obj.close()
                    #     # print("text file successfully posted")
                    # except:
                    #     print("Unable to open ", file_path)
            except:
                pass
                # print(info, value)
                # print("no file")
                # print("Unable to create file")
            info_dict['value'] = value
            # print("Info_dict: ")
            # print(info_dict)

            if info_dict['filename']:
                print("File Detected")
            try:
                if not info_dict['filename']:
                    print(info, value)
                    temp_dict[info_dict['name']] = info_dict['value']
            except:
                return 400
            # print()

        # print("Object to append: ", temp_dict)
        json_obj = json.dumps(temp_dict)
        json_obj = json.loads(json_obj)
        json_obj['Year'] = int(json_obj['Year'])
        json_obj['MIS'] = int(json_obj['MIS'])

        # print("json_obj: ", json_obj)

        if os.path.exists(uri):
            # print("File exits")
            if os.access(path=uri, mode=os.R_OK):
                fp = open(uri, "r")
                obj = json.load(fp)
            else:
                return 403
        else:
            # print("File does not exist")
            obj = []

        obj.append(json_obj)
        # print("List to append: ", obj)

        if os.path.exists(uri):
            # print("File exits")
            if os.access(path=uri, mode=os.W_OK):
                try:
                    fp = open(uri, "w")
                    json.dump(obj, fp)
                    return 200
                except:
                    return 500
            else:
                return 403
        else:
            # print("File does not exist")
            try:
                fp = open(uri, "w")
                json.dump(obj, fp)
                return 200
            except:
                return 500

        # try:
        #     fp = open(uri, "w")
        #     json.dump(obj, fp)
        #     return 200
        # except:
        #     print("Unable to open file")
        #     return 500

    return 500


def get_modification_time(file_name):
    return strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(os.path.getmtime(file_name)))


def get_data(file_path, file_extension=None, queries=None):
    # print("in get_data()-> file_path:", file_path, " file_extension:", file_extension, "queries:", queries)

    if file_extension in ["ico", "jpeg", "jpg"]:
        file_obj = open(file_path, 'rb')
        image_raw = file_obj.read()
        file_obj.close()
        return (get_modification_time(file_path), image_raw)

    elif file_extension in ["html", "json", "js"]:
        if file_extension == "json" and queries:
            file_obj = open(file_path, "r")
            # obj_list is list of objects (json)
            obj_list = json.load(file_obj)
            file_obj.close()
            to_return = []
            for obj in obj_list:
                # print("obj: ", obj)
                flag = 1
                for attr in queries:
                    # print("attr: ", attr, "Value: ", queries[attr])
                    # print("obj[attr]: ", obj[attr])
                    if str(obj[attr]) != str(queries[attr]):
                        # print("found")
                        flag = 0
                if flag == 1:
                    # print("Object Found")
                    return (None, json.dumps(obj))
            return (None, "No Data Available")
        else:
            file_obj = open(file_path, "r")
            text_data = file_obj.read()
            file_obj.close()
            return (get_modification_time(file_path), text_data)
