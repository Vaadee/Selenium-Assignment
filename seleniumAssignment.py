import time, requests
from selenium import webdriver
import numpy as np
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

masterLoadData = [
    [
        "Website",
        "Link",
        "Broadband Provider",
        "Link Load Time (Average of 5 tries)",
        "Link is dead or timed out (Y/N)",
    ]
]
# masterSiteData = [
#     [
#         "Website",
#         "Broadnand Provider",
#         "Average Link Load Time",
#         "Number of Dead Links/ Time Outs",
#         "Number of Working Links",
#         "Website Score",
#     ]
# ]

websites = [
    "https://nrega.nic.in/netnrega/home.aspx",
    "https://www.usa.gov/",
    "https://www.isro.gov.in/",
    "https://www.bits-pilani.ac.in/",
    "https://medium.com/",
    # "https://swd.bits-hyderabad.ac.in/",
    # "https://cms.bits-hyderabad.ac.in/login/index.php",
]

driver = webdriver.Chrome()
driver.minimize_window()

for site in websites:
    driver.get(site)
    listOfWebsites = []
    # siteData = []
    loadData = []
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

    bar = progressbar.ProgressBar(max_value=len(links), widgets=widgets).start()
    for link in listOfWebsites:
        bar.update(listOfWebsites.index(link))
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
                frontendPerformance_calc = domComplete - responseStart
                tempTime += frontendPerformance_calc
            if requests.head(link).status_code in range(200, 400):
                countValid += 1
                status = "N"
            else:
                countInvalid += 1
                status = "Y"
            loadData.append([site, link, "ACT-Fibernet", tempTime / 5, status])
        except:
            countInvalid += 1
            status = "Y"
            loadData.append([site, link, "ACT-Fibernet", "NA", status])

    print(
        "\nComplete.\nThe count of valid links in {} is {} and invalid links is {}".format(
            site, countValid, countInvalid
        )
    )

    # averageLinkLoadTime = loadData[1:, 3].mean()
    # masterSiteData.append(
    #     [site, "ACT Fibernet", averageLinkLoadTime, countInvalid, countValid, 0]
    # )
    for rowTemp in loadData:
        masterLoadData.append(rowTemp)

driver.quit()
# masterSiteData = np.array(masterSiteData, dtype=dtypeMasterSiteData)
# for row in masterSiteData:
#     A = (row[2] - masterSiteData[1:, 2].min()) / (
#         masterSiteData[1:, 2].max() - masterSiteData[1:, 2].min()
#     )
#     B = row[3] / (row[3] + row[4])
#     row[5] = (A + B) / 2
dataFrameLoadData = pd.DataFrame(masterLoadData)
# dataFrameSiteData = pd.DataFrame(masterSiteData)
dataFrameLoadData.to_csv("loadData.csv", index=False)
# dataFrameSiteData.to_csv("siteData.csv".format)
