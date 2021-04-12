import time, requests
from selenium import webdriver
from selenium.webdriver.common import keys
from tqdm import tqdm

driver = webdriver.Chrome()
driver.maximize_window()

driver.get("https://www.bits-pilani.ac.in/")
search = driver.find_element_by_xpath("//*[@id='gsc-i-id1']")
search.sendkeys("Hello")
driver.find_element_by_xpath(
    "//*[@id='___gcse_0']/div/form/table/tbody/tr/td[2]/button"
).click()

listOfWebsites = []
countValid = countInvalid = 0
links = driver.find_elements_by_css_selector("a")

for link in links:
    if link.get_attribute("href") not in listOfWebsites:
        listOfWebsites.append(link.get_attribute("href"))

for link in links:
    try:
        r = requests.head(link.get_attribute("href"))
        if r.status_code in range(200, 400):
            countValid += 1
            # driver.get(link.get_attribute("href"))
            # responseStart = driver.execute_script(
            #     "return window.performance.timing.responseStart"
            # )
            # domComplete = driver.execute_script(
            #     "return window.performance.timing.domComplete"
            # )
            # frontendPerformance_calc = domComplete - responseStart
            # print(
            #     "Status of site '{}' is {}. And the link load time is: {}".format(
            #         link.get_attribute("href"), r.status_code, frontendPerformance_calc
            #     )
            # )
            print(link.get_attribute("href"))
        else:
            countInvalid += 1
    except:
        countInvalid += 1
        print("Request Not Found")
print("The website contaings {} links".format(len(links)))
print(
    "The number of valid links are {} and invalid links are {}".format(
        countValid, countInvalid
    )
)

driver.quit()