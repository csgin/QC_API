def return_test_instance_dictionary(test_instance):
    test_instance_dictionary = {}
    for fields in test_instance.findall("Fields"):
        fields = fields.findall("Field")
        for i in fields:
            test_instance_dictionary[i.attrib["Name"]] = i[0].text
    return test_instance_dictionary

def return_list_of_dictionary_with_test_instances(test_instances):
    return [return_test_instance_dictionary(instance) for instance in test_instances]