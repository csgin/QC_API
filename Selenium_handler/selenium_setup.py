from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def return_driver():
    '''Please provide complete path to chromedriver'''
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(r".....\chromedriver.exe", options=options)
    driver.get("http://10.42.109.163/CIT.WRO")
    return driver

