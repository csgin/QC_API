from Selenium_handler.Selenium_scraper import colect_data_from_WCTO
from Setting import test_sets_id, settings
from API_connection_handler.connection_handler import conn_handler
from XML_parser.xml_handler import xml_handler
from Colect_data_scripts.common import return_list_of_dictionary_with_test_instances


class CITData():
    def __init__(self):
        self.WCTO_data = colect_data_from_WCTO()
        self.test_lines = test_sets_id.cit_test_lines
        self.feature = settings.feature_sett
        self.competence = settings.competence_sett
        self.expected_build = self.WCTO_data['build']
        self.qc_project = settings.cit_qc_project_sett
        self.qc_domain = settings.cit_qc_domain_sett

    def collect_data_from_qc(self):
        data_from_qc = {}
        connection = conn_handler()
        connection.open_connection()
        for key in self.test_lines.keys():
            response = connection.send_request(self.test_lines[key], "status", "user-03", "name", domain=self.qc_domain,
                                           project=self.qc_project)
            data_from_qc[key] = response
        connection.close_connection()
        return data_from_qc

    def check_data_from_qc_and_return_json(self, data_from_qc):
        json_table = []
        xml_handle = xml_handler()
        for key in data_from_qc.keys():
            response = xml_handle.parse_to_xml(data_from_qc[key])
            xml_handle.save_as_xml(response, "cit_report")
            file = xml_handle.convert_xml_to_element_tree("cit_report")
            test_instances = xml_handle.return_xml_objects_list_by_name(file, "Entity")
            test_instances = return_list_of_dictionary_with_test_instances(test_instances)
            no_of_wrong_filled_tc = self.check_test_instances(test_instances)
            if len(no_of_wrong_filled_tc) > 0:
                print("\nTESTLINE NAME: ", key, " NO OF WRONG FILLED  TI IN QC: ", len(no_of_wrong_filled_tc), "  \n")
                json_table.append([key, len(no_of_wrong_filled_tc)])
                for i in no_of_wrong_filled_tc:
                    print(f"        {i}")
        return json_table

    def apply_not_applicable_from_WCTO(self, json_table):
        not_applicable = self.WCTO_data['not_applicable']
        if len(not_applicable) < 1:
            return json_table
        for na_test_line in not_applicable.keys():
            for test_line in json_table:
                if na_test_line.lower() in test_line[0].lower():
                    json_table.pop(json_table.index(test_line))
        return json_table

    def apply_still_running_status_from_WCTO(self, json_table):
        running = self.WCTO_data['running']
        if len(running) < 1:
            return json_table
        for running_test_line in running.keys():
            for test_line in json_table:
                if running_test_line.lower() in test_line[0].lower():
                    test_line[0] = "RUNNING_" + str(test_line[0])
                    test_line[1] = 0
                    test_line[2] = 0
        return json_table

    def apply_no_runs_from_WCTO(self, json_table):
        no_runs = self.WCTO_data['no_runs']
        if len(no_runs) < 1:
            return json_table
        for nr_test_line in no_runs.keys():
            for test_line in json_table:
                if nr_test_line.lower() in test_line[0].lower():
                    test_line[1] = test_line[1] - no_runs[nr_test_line]
                    test_line.append(no_runs[nr_test_line])
        return json_table

    def check_json_table_before_save(self, json_table):
        for tl in json_table:
            if len(tl) < 3:
                tl.append(0)
        return json_table

    def check_test_instances(self, test_instances):
        return [instance['name'] for instance in test_instances if
                self.check_if_tc_is_marked_correctly_in_qc(instance) == False]

    def check_if_tc_is_marked_correctly_in_qc(self, instance):
        if self.feature in instance['name'] and instance['status'] != "N/A" and instance['user-03'] != self.expected_build:
            return False
        if self.competence not in instance['name'] or instance['status'] == "N/A":
            return None
        if instance['user-03'] == self.expected_build and self.competence in instance['name']:
            return True
        else:
            return False

    def collect_data(self):
        xml_handle = xml_handler()
        data_from_qc = self.collect_data_from_qc()
        json_table = self.check_data_from_qc_and_return_json(data_from_qc)
        json_table = self.apply_not_applicable_from_WCTO(json_table)
        json_table = self.apply_no_runs_from_WCTO(json_table)
        json_table = self.apply_still_running_status_from_WCTO(json_table)
        json_table = self.check_json_table_before_save(json_table)
        xml_handle.save_as_json(json_table, "cit.json")
