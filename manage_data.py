import csv
import json


def display_file():
    fp = open("src/data/data_file1.json", "r")
    data = json.load(fp)
    print(data)


def put_data(data, uri=None):
    pass


def delete_data(data, uri=None):
    pass


def add_data(data, uri=None):
    # print("in add_data file: ", data)
    fp = open("src/data/data_file1.json", "r")
    obj = json.load(fp)
    data['Year'] = int(data['Year'])
    data['MIS'] = int(data['MIS'])
    obj.append(data)
    fp = open("src/data/data_file1.json", "w")
    json.dump(obj, fp)
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
