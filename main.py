from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


PROGRAM_PREFIX = "[Parental_Controller]"

class ParentalControl:
    ENABLED = True
    DISABLED = False

    def __init__(self):
        self.driver = webdriver.Firefox()
        self._patch_driver()

    def __del__(self):
        self.driver.quit()

    def set_parental_control_to(self, status):
        self._login()
        self._open_parental_control_tab()

        if self._is_parental_control_enabled() != status:
            self._toggle_parental_control()

    def _toggle_parental_control(self):
        self._safe_click("ParentCtr_en")
        self._safe_click("saveClkBtn")

    def _login(self):
        self.driver.get('http://192.168.1.1')
        username = self.driver.find_element_by_id("userName")
        username.send_keys("admin")
        password = self.driver.find_element_by_id("pcPassword")
        password.send_keys("admin")
        self._safe_click("loginBtn")

    def _wait_for_element(self, id_):
        while True:
            try:
                return self.driver._find_element_by_id(id_)
            except NoSuchElementException:
                pass

    def _safe_click(self, id):
        WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((By.ID, id))).click()

    def _patch_driver(self):
        self.driver._find_element_by_id = self.driver.find_element_by_id
        self.driver.find_element_by_id = self._wait_for_element

    def _is_parental_control_enabled(self):
        return self.driver.find_element_by_id("ParentCtr_en").is_selected()

    def _open_parental_control_tab(self):
        self._safe_click("menu_pc")


while True:
    parental_control = ParentalControl()
    try:
        parental_control.set_parental_control_to(ParentalControl.ENABLED)
    except Exception:
        print(PROGRAM_PREFIX + "exception occurred")
    finally:
        parental_control.__del__()

    # sleep(60)
