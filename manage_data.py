import csv
import json
import os


def display_file():
    fp = open("src/data/data_file1.json", "r")
    data = json.load(fp)
    print(data)


def put_data(data, uri=None):
    pass


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

        elif file_extension in ["html", "jpeg", "png", "jpg"]:
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


def post_data(uri, msg_body, file_extension, content_type):
    print("in post_data : uri: ", uri, " msg_body: ",
          msg_body, " file_extension: ", file_extension, " Content-type: ", content_type)
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

    # fp = open("src/data/data_file1.json", "r")
    # obj = json.load(fp)
    # data['Year'] = int(data['Year'])
    # data['MIS'] = int(data['MIS'])
    # obj.append(data)
    # fp = open("src/data/data_file1.json", "w")
    # json.dump(obj, fp)
    return


def get_data(file_path, file_extension=None, queries=None):
    print("in get_data()-> file_path:", file_path, " file_extension:",
          file_extension, "queries:", queries)

    if file_extension in ["ico", "jpeg", "jpg"]:
        file_obj = open(file_path, 'rb')
        image_raw = file_obj.read()
        return image_raw

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
                        return json.dumps(obj)
            return "No Data Available"

        file_obj = open(file_path, "r")
        text_data = file_obj.read()
        return text_data


# display_file()
