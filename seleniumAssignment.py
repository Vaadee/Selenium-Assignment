import time, requests
from selenium import webdriver
import pandas as pd
import progressbar
import csv

widgets = [
    " [",
    progressbar.Timer(format="elapsed time: %(elapsed)s"),
    "] ",
    progressbar.Bar("#"),
    " (",
    progressbar.ETA("-"),
    ") ",
]

masterLoadData = []
masterSiteData = []

websites = [
    "https://nrega.nic.in/netnrega/home.aspx",
    "https://www.usa.gov/",
    "https://www.isro.gov.in/",
    "https://www.bits-pilani.ac.in/",
    "https://medium.com/",
    # "https://cms.bits-hyderabad.ac.in/login/index.php",
    # "https://swd.bits-hyderabad.ac.in/",
]

driver = webdriver.Chrome()
driver.maximize_window()

time = maxTime = 0
minTime = 99999999

for site in websites:
    driver.get(site)
    listOfWebsites = []
    siteData = []
    loadData = []
    time = 0
    countValid = countInvalid = 0
    links = driver.find_elements_by_css_selector("a")

    for testLink in links:
        # if testLink.get_attribute("href") not in listOfWebsites:
        listOfWebsites.append(testLink.get_attribute("href"))
    print(
        "Currently testing site {}, the total number of links is {} so this could take a while.".format(
            site, len(listOfWebsites)
        )
    )

    bar = progressbar.ProgressBar(
        max_value=len(listOfWebsites), widgets=widgets
    ).start()
    for link in listOfWebsites:
        try:
            alert = Alert(driver)
            alert.dismiss()
        except:
            pass
        try:
            tempTime = 0
            for count in range(5):
                driver.get(link)
                responseStart = driver.execute_script(
                    "return window.performance.timing.responseStart"
                )
                domComplete = driver.execute_script(
                    "return window.performance.timing.domComplete"
                )
                while domComplete == 0:
                    domComplete = driver.execute_script(
                        "return window.performance.timing.domComplete"
                    )
                frontendPerformance_calc = domComplete - responseStart
                tempTime += frontendPerformance_calc
            if requests.head(link).status_code in range(200, 400):
                countValid += 1
                status = "N"
            else:
                countInvalid += 1
                status = "Y"
            masterLoadData.append([site, link, "ACT-Fibernet", tempTime / 5, status])
            # print("[", site, link, "ACT-Fibernet", tempTime / 5, status, "]")
            time += tempTime / 5
        except:
            countInvalid += 1
            status = "Y"
            masterLoadData.append([site, "NA", "ACT-Fibernet", "NA", status])
            # print("[", site, link, "ACT-Fibernet", "NA", status, "]")
        bar.update(listOfWebsites.index(link))
    print(
        "\nComplete.\nThe count of valid links in {} is {} and invalid links is {}".format(
            site, countValid, countInvalid
        )
    )
    averageLinkLoadTime = time / countValid
    if averageLinkLoadTime < minTime:
        minTime = averageLinkLoadTime
    if averageLinkLoadTime > maxTime:
        maxTime = averageLinkLoadTime
    masterSiteData.append(
        [
            site,
            "ACT Fibernet",
            averageLinkLoadTime,
            countInvalid,
            countValid,
        ]
    )

driver.quit()
print(maxTime, minTime)
for row in masterSiteData:
    A = (float(row[2]) - minTime) / (maxTime - minTime)
    B = float(row[3]) / (float(row[3]) + float(row[4]))
    row.append((A + B) / 2)

masterLoadData = pd.DataFrame(
    masterLoadData,
    columns=[
        "Website",
        "Link",
        "Broadband Provider",
        "Link Load Time (Average of 5 tries)",
        "Link is dead or timed out (Y/N)",
    ],
)
masterSiteData = pd.DataFrame(
    masterSiteData,
    columns=[
        "Website",
        "Broadnand Provider",
        "Average Link Load Time",
        "Number of Dead Links/ Time Outs",
        "Number of Working Links",
        "Website Score",
    ],
)
masterSiteData.sort_values(by=["Website Score"])
masterLoadData.to_csv(
    "loadData.csv",
    index=False,
)
masterSiteData.to_csv(
    "siteData.csv",
    index=False,
)
