from Selenium_handler.selenium_setup import return_driver
from Setting import settings

def _get_tl_names_from_WCTO(driver):
    frame_xpath = "//div[@class='grid-container']"
    frames = driver.find_elements_by_xpath(frame_xpath)
    return [frame.text.split()[0].split("-")[-1] for frame in frames]

def _get_build_name_selenium(driver):
    elements = driver.find_elements_by_xpath("//div[@class='base_sw']")
    for element in elements:
        if len(element.text) > 6 and "SBTS00" in element.text:
            return element.text

def _get_no_runs_for_each_TL(driver, test_lines, list_of_keywords):
    no_runs_dict = {}
    for tl_name in test_lines:
        try:
            no_runs = driver.find_elements_by_xpath(
                f"//div[@class='grid-container' and descendant::a[contains(text(), '{tl_name}')]]//a[@class='scheduled']")
            for no_run in no_runs:
                for key_word in list_of_keywords:
                    if key_word in no_run.get_attribute('innerHTML'):
                        if tl_name not in no_runs_dict.keys():
                            no_runs_dict[tl_name] = 1
                        else:
                            no_runs_dict[tl_name] += 1
        except:
            continue
    return no_runs_dict

def _get_na_test_lines(driver, test_lines):
    na_dict = {}
    for tl_name in test_lines:
        tl_status = driver.find_element_by_xpath(
            f"//div[@class='grid-container' and descendant::a[contains(text(), '{tl_name}')]]//button[@class='dropbtn btn-small']")
        if tl_status.text == "N/A":
            na_dict[tl_name] = "N/A"
    return na_dict

def _get_running_tl(driver, test_lines):
    running_tl = {}
    for tl_name in test_lines:
        try:
            if_tl_still_run = driver.find_element_by_xpath(
                f"//div[@class='grid-container' and descendant::a[contains(text(), '{tl_name}')]]//div[@title='running_tc']")
            if if_tl_still_run:
                running_tl[tl_name] = "still_running"

        except:
                continue
    return running_tl

def colect_data_from_WCTO():
    driver = return_driver()
    test_lines = _get_tl_names_from_WCTO(driver)
    build = _get_build_name_selenium(driver)
    no_runs = _get_no_runs_for_each_TL(driver, test_lines, [settings.competence_sett, settings.feature_sett])
    not_applicable = _get_na_test_lines(driver,test_lines)
    running = _get_running_tl(driver, test_lines)
    driver.quit()
    return {"build" : build,
            "no_runs" : no_runs,
            "not_applicable" : not_applicable,
            "running" : running}

