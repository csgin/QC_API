from Setting import test_sets_id, settings
from API_connection_handler.connection_handler import conn_handler
from XML_parser.xml_handler import xml_handler
from datetime import date
from Colect_data_scripts.common import return_list_of_dictionary_with_test_instances


class CRTData():
    def __init__(self):
        self.test_lines = test_sets_id.wro_8_CRT
        self.reference_date = settings.crt_round_date_sett

    def convert_str_to_date(self, string_date):
        return date(*map(int, string_date.split('-')))

    def check_test_instances(self, test_instances):
        return [instance['name'] for instance in test_instances if
                self.check_if_tc_is_marked_correctly_in_qc(instance) == False]

    def check_if_tc_was_executed_during_this_round(self, qc_date, tc_status, date_to_check_regression):
        if tc_status == "N/A":
            return None
        qc_dat = self.convert_str_to_date(qc_date)
        input = self.convert_str_to_date(date_to_check_regression)
        if qc_dat < input: return False
        if qc_dat >= input and tc_status == "No Run": return False
        if qc_dat >= input: return True

    def collect_CRT_data_from_qc(self):
        data_from_qc = {}
        connection = conn_handler()
        connection.open_connection()
        for key in self.test_lines.keys():
            response = connection.send_request(self.test_lines[key],"status",
                                               "user-03", "name", "exec-date")
            data_from_qc[key] = response
        connection.close_connection()
        return data_from_qc

    def collect_data(self):
        json_table = []
        xml_handle = xml_handler()
        data_from_qc = self.collect_CRT_data_from_qc()
        for key in data_from_qc.keys():
            response = xml_handle.parse_to_xml(data_from_qc[key])
            xml_handle.save_as_xml(response, "cit_report")
            file = xml_handle.convert_xml_to_element_tree("cit_report")
            test_instances = xml_handle.return_xml_objects_list_by_name(file, "Entity")
            test_instances = return_list_of_dictionary_with_test_instances(test_instances)
            counter = 0
            print("\nCRT TESTLINE NAME: ", key)
            for i in test_instances:
                if i['status'] == "N/A" or i['status'] == "Failed" or i['status'] == "Blocked":
                    continue
                was_executed = self.check_if_tc_was_executed_during_this_round(i['exec-date'], i['status'], self.reference_date)
                if not was_executed or i['status'] != "Passed":
                    counter += 1
                    print(
                        f"Execution date: {i['exec-date']} TC status in QC: {i['status']} Build {i['user-03']} TC name {i['name']}")
            print(counter)
            json_table.append([key, counter])
        xml_handle.save_as_json(json_table, "crt.json")


