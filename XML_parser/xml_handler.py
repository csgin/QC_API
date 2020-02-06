import xml.etree.ElementTree as ET
import xml.dom.minidom
import json
import os.path

class xml_handler():
    def __init__(self):
        self.directory_json = './Jsons/'
        if not os.path.isdir(self.directory_json):
            os.mkdir(self.directory_json)

        self.directory_xml = './XML/'
        if not os.path.isdir(self.directory_xml):
            os.mkdir(self.directory_xml)

    def parse_to_xml(self, object):
        xml_form = xml.dom.minidom.parseString(object.text)
        xml_form = xml_form.toprettyxml()
        return xml_form

    def save_as_xml(self, object, file_name):
        with open(f"{self.directory_xml}{file_name}", "wb") as file:
            file.write(object.encode())

    def convert_xml_to_element_tree(self, xml_filename):
        return ET.parse(xml_filename).getroot()

    def return_xml_objects_list_by_name(self, file, object_name):
        return file.findall(object_name)

    def save_as_json(self, object, file_name):
        with open(f"{self.directory_json}{file_name}", 'w') as f:
            json.dump(object, f, ensure_ascii=False)