from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime

import platform

if platform.system() == "Linux":
    from systemd import journal

    print = journal.send

PROGRAM_PREFIX = "[Parental_Controller] "
SLEEP_TIME = 5 * 60


class ParentalControlController:
    ENABLED = True
    DISABLED = False

    def __init__(self):
        options = Options()
        options.headless = True
        options.add_argument("window-size=1920,1080")

        self.driver = webdriver.Firefox(options=options)
        self._patch_driver()

        self.is_at_the_parental_control_page = False

    def __del__(self):
        self.driver.quit()

    def set_parental_control_to(self, status):
        if self.is_enabled() != status:
            self._toggle_parental_control()

        return self.is_enabled()

    def is_enabled(self):
        if not self.is_at_the_parental_control_page:
            self._login()
            self._open_parental_control_tab()
            self.is_at_the_parental_control_page = True

        return self.driver.find_element_by_id("ParentCtr_en").is_selected()

    def is_enabled_str(self):
        return "ENABLED" if self.is_enabled() else "DISABLED"

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

    def _open_parental_control_tab(self):
        self._safe_click("menu_pc")


class Printer:
    @staticmethod
    def print_we_just_changed_state(now, parental_control):
        print(
            PROGRAM_PREFIX +
            f"parental control is set to {parental_control.is_enabled_str()},"
            f" now is " + now.__str__()
        )

    @staticmethod
    def print_we_are_idle(now, parental_controller):
        print(
            PROGRAM_PREFIX +
            f"going to sleep for {SLEEP_TIME} secs, now is " + now.__str__() +
            "  parental control is:" + parental_controller.is_enabled_str()
        )

    @staticmethod
    def print_we_just_started(now, parental_controller):
        print(
            PROGRAM_PREFIX +
            f"program started, now is " + now.__str__() +
            "  parental control set to:" + parental_controller.is_enabled_str()
        )

    @staticmethod
    def print_exception(e):
        print(PROGRAM_PREFIX + "exception occurred: " + e.__repr__())


def idle(now: datetime, parental_controller: ParentalControlController):
    Printer.print_we_are_idle(now, parental_controller)
    sleep(SLEEP_TIME)


def internet_should_be_disconnected(now: datetime):
    return now.hour >= 22 or now.hour < 7


def main():
    parental_control = ParentalControlController()
    parental_control_state = parental_control.is_enabled()
    Printer.print_we_just_started(datetime.now(), parental_control)
    parental_control.__del__()

    while True:
        try:
            parental_control = ParentalControlController()
            now = datetime.now()

            if internet_should_be_disconnected(now) and parental_control_state == ParentalControlController.DISABLED:
                parental_control = ParentalControlController()
                parental_control_state = parental_control.set_parental_control_to(ParentalControlController.ENABLED)
                Printer.print_we_just_changed_state(now, parental_control)

            elif not internet_should_be_disconnected(now) and \
                    parental_control_state == ParentalControlController.ENABLED:
                parental_control = ParentalControlController()
                parental_control_state = parental_control.set_parental_control_to(ParentalControlController.DISABLED)
                Printer.print_we_just_changed_state(now, parental_control)

            idle(now, parental_control)
            parental_control.__del__()
        except Exception as e:
            Printer.print_exception(e)
            parental_control.__del__()
        finally:
            parental_control.__del__()


if __name__ == "__main__":
    main()
