import requests
from requests.auth import HTTPBasicAuth
import urllib3
from Setting import settings

class conn_handler():
    def __init__(self):
        self.hpqc_server = "https://qc12-prod.int.net.nokia.com/qcbin/"
        self.username = settings.user_sett['username']
        self.password = settings.user_sett['password']
        urllib3.disable_warnings()

    def open_connection(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.post(self.hpqc_server + "authentication-point/authenticate?login-form-required=y",
                     auth=HTTPBasicAuth(self.username, self.password))
        self.session.post(self.hpqc_server + "rest/site-session")

    def send_request(self, test_set_id, *args,  domain="MN_CDS", project="SRAN_BTS_IV"):
        fields = ""
        for i in args:
            fields += i + ","
        response = self.session.get(
            self.hpqc_server + f"rest/domains/{domain}/projects/{project}/test-instances?fields=" + fields[:-1] + "&query={cycle-id[=" + str(
                test_set_id) + "];}")
        return response

    def close_connection(self):
        requests.session().close()
