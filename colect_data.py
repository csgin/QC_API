from Colect_data_scripts import CIT, CRT
from Colect_data_scripts import MR
import time

cit = CIT.CITData()
crt = CRT.CRTData()
while True:
    MR.colect_data()
    cit.collect_data()
    crt.collect_data()
    time.sleep(300)
