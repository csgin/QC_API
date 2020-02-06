from Setting import test_sets_id, settings
from API_connection_handler.connection_handler import conn_handler
from XML_parser.xml_handler import xml_handler
from datetime import date

def convert_str_to_date(string_date):
    return date(*map(int, string_date.split('-')))

def return_test_instance_dictionary(test_instance):
    test_instance_dictionary = {}
    for fields in test_instance.findall("Fields"):
        fields = fields.findall("Field")
        for i in fields:
            try:
                test_instance_dictionary[i.attrib["Name"]] = i[0].text
            except:
                pass
    return test_instance_dictionary

def return_list_of_dictionary_with_test_instances(test_instances):
    return [return_test_instance_dictionary(instance) for instance in test_instances]

def check_if_tc_was_executed_in_this_round(qc_date, tc_status, date_to_check_regression):
    if tc_status == "N/A":
        return None
    qc_dat = convert_str_to_date(qc_date)
    input = convert_str_to_date(date_to_check_regression)
    if qc_dat < input: return False
    if qc_dat > input: return True

def check_tc(ti, date_to_check_regression):
    to_do = []
    passed = []
    failed = []
    na = []
    for instance in ti:
        if instance['status'] == "No Run":
            to_do.append([instance['name'], instance['status']])
        elif instance['status'] == "N/A":
            na.append([instance['name'], instance['status']])
        else:
            status = check_if_tc_was_executed_in_this_round(instance['exec-date'], instance['status'], date_to_check_regression)
            if status and instance['status'] == "Passed":
                passed.append([instance['name'], instance['exec-date'], instance['status']])
            elif status == "Failed" and instance['status'] == "Failed":
                failed.append([instance['name'], instance['exec-date'], instance['status']])
            else:
                to_do.append([instance['name'], instance['exec-date'], instance['status']])
    return to_do, passed, failed

def colect_data():
    wro8regtl = test_sets_id.wro_8_manual_reg_test_lines
    ch = conn_handler()
    xml_handle = xml_handler()
    ch.open_connection()
    manual_regression_start = settings.manual_regression_start_date_sett
    json_table_no_run = []
    json_table_failed = []
    json_table_passed = []

    for key in wro8regtl.keys():
        response = ch.send_request(wro8regtl[key], "name", "status", "exec-date")
        response = xml_handle.parse_to_xml(response)
        xml_handle.save_as_xml(response, "report")
        file = xml_handle.convert_xml_to_element_tree("report")
        test_instances = xml_handle.return_xml_objects_list_by_name(file, "Entity")
        test_instances = return_list_of_dictionary_with_test_instances(test_instances)
        to_do, passed, failed = check_tc(test_instances, str(manual_regression_start))
        json_table_no_run.append([key, len(to_do)])
        json_table_passed.append([key, len(passed)])
        json_table_failed.append([key, len(failed)])

    xml_handle.save_as_json(json_table_no_run, "manual_no_run.json")
    xml_handle.save_as_json(json_table_failed, "manual_failed.json")
    xml_handle.save_as_json(json_table_passed, "manual_passed.json")
    ch.close_connection()
