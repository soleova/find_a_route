import re
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FindRoute:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def open_page(self, url):
        assert isinstance(url, str)
        r = requests.get(url)
        # quick check if the website throws any of the client or server errors (4xx and 5xx errors)
        if r.status_code < 400:
            self.driver.get(url)
            self.driver.maximize_window()
        else:
            print("HTTP error: " + str(r.status_code))
            self.driver.close()
            raise Exception

    def search_route(self, src, dst):
        assert isinstance(src, str)
        assert isinstance(dst, str)
        directions = self.wait.until(EC.element_to_be_clickable((By.ID, 'searchbox-directions')))
        directions.click()
        src_elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-0']//input")))
        src_elem.send_keys(src)
        src_elem.send_keys(Keys.RETURN)
        print(src + " is entered as a starting point")
        dst_elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='directions-searchbox-1']//input")))
        dst_elem.send_keys(dst)
        dst_elem.send_keys(Keys.RETURN)
        print(dst + " is entered as a destination")

    def select_type_of_drive(self):
        # choose drive by car from the possible options
        options_element = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'section-directions')]/span")))
        options_element.click()
        print("Drive by car is selected")

    def avoid_highways(self):
        # choose to avoid highways from the possible options
        check_to_avoid = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//label[@for='pane.directions-options-avoid-highways']")))
        check_to_avoid.click()
        print("Avoid highways is selected")
        sleep(2)

    def find_longest_route_with_details(self):
        # find all possible routes
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'section-directions-trip-description')]")))
        all_routes = self.driver.find_elements_by_xpath(
            "//div[contains(@class, 'section-directions-trip-description')]")

        self.longest_distance = re.search("(\d+)\s*km", all_routes[0].text).group(1)

        # initially setting the first route to be clicked
        global item_to_click
        item_to_click = all_routes[0]
        for r in all_routes:
            curr_len = re.search("(\d+)\s*km", r.text).group(1)
            print("Current distance is " + curr_len + " km")
            if curr_len > self.longest_distance:
                # if there is a longer distance, set that distance as longest and choose that item
                self.longest_distance = curr_len
                item_to_click = r
                # extract hours and minutes from the duration
                duration = re.search("(\d+)\s*\w+\s*(\d*)\w*", r.text)
                self.duration_hours = duration.group(1)
                self.duration_minutes = duration.group(2)

        print("Longest distance found - " + self.longest_distance + " km")
        print("Duration - " + self.duration_hours + " hours " + self.duration_minutes + " minutes")

        item_to_click.click()  # first click on the element expands it
        sleep(1)
        item_to_click.click()  # second click opens the details page
        print("Details page opened")

    def check_presence_of_distance_and_time(self):
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class, 'section-trip-summary-title')]")))
        summary = self.driver.find_element_by_xpath(
            "//h1[contains(@class, 'section-trip-summary-title')]")

        longest_distance_details = re.search("(\d+)\s*km", summary.text).group(1)
        duration_details = re.search("(\d+)\s*\w+\s*(\d*)\w*", summary.text)
        duration_hours_details = duration_details.group(1)
        duration_minutes_details = duration_details.group(2)

        print("Distance on details page - " + longest_distance_details + " km")
        print("Duration on details page - " + duration_hours_details + " hours "
              + duration_minutes_details + " minutes")

        if summary:
            print("Summary with duration and distance present: PASS")
            if self.duration_hours == duration_hours_details \
                    and self.duration_minutes == duration_minutes_details \
                    and self.longest_distance == longest_distance_details:
                print("Duration and distance correct: PASS")
            else:
                print("Duration and distance correct: FAIL")
        else:
            print("Duration and distance presence on details page: FAIL")

    def close(self):
        # wait a little so that we can see the final results of our test in our browser and then close the browser
        sleep(5)
        self.driver.close()


test_route = FindRoute()
test_route.open_page('https://maps.google.com')
test_route.search_route('Budapest', 'Belgrade')
test_route.select_type_of_drive()
test_route.avoid_highways()
test_route.find_longest_route_with_details()
test_route.check_presence_of_distance_and_time()
test_route.close()
