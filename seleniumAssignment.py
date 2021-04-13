# Importing required libraries
import time, requests, progressbar, csv, pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Initializing the progressbar
widgets = [
    " [",
    progressbar.Timer(format="elapsed time: %(elapsed)s"),
    "] ",
    progressbar.Bar("#"),
    " (",
    progressbar.ETA("-"),
    ") ",
]

# Initializing the required lists and variables
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
timeCalc = maxTime = 0
minTime = 99999999

# Initializing selenium webDriver
options = Options()
options.add_argument("ignore-certificate-errors")
options.add_argument("--allow-running-insecure-content")

driver = webdriver.Chrome(options=options)
driver.maximize_window()

# Loop that runs the code on all the websites provided in the list above
for site in websites:
    # Initializing temperary variables for the loop
    driver.get(site)
    listOfWebsites = []
    websiteCount = []
    siteData = []
    loadData = []
    timeCalc = 0
    countValid = countInvalid = 0
    links = driver.find_elements_by_css_selector("a")

    # Checking if the list of links is less than 100. (Helpful for websites with lazy scroll)
    while len(links) < 100:
        try:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            links = driver.find_elements_by_css_selector("a")
            time.sleep(0.5)
        except:
            break

    # Capturing unique set of links from the main website. This helps reduce the redundency in testing the same link multiple times.
    for testLink in links:
        if testLink.get_attribute("href") not in listOfWebsites:
            listOfWebsites.append(testLink.get_attribute("href"))
            websiteCount.append(1)
        else:
            index = listOfWebsites.index(testLink.get_attribute("href"))
            websiteCount[index] += 1

    # Prints the current state of the website to the console.
    print(
        "Currently testing site {}, the total number of links is {} so this could take a while.".format(
            site, len(links)
        )
    )

    # Calling the progressbar
    bar = progressbar.ProgressBar(
        max_value=len(listOfWebsites), widgets=widgets
    ).start()

    # Loop that works with each sublink in the main website
    for link in listOfWebsites:
        index = listOfWebsites.index(link)
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
                countValid += 1 * websiteCount[index]
                status = "N"
            else:
                countInvalid += 1 * websiteCount[index]
                status = "Y"
            masterLoadData.append([site, link, "ACT-Fibernet", tempTime / 5, status])
            timeCalc += (tempTime / 5) * websiteCount[index]
        except:
            countInvalid += 1 * websiteCount[index]
            status = "Y"
            masterLoadData.append([site, "NA", "ACT-Fibernet", "NA", status])

        # Updates the progressbar after some interval of time
        bar.update(listOfWebsites.index(link))

    # Prints the current state of the program to console
    print(
        "\nComplete.\nThe count of valid links in {} is {} and invalid links is {}".format(
            site, countValid, countInvalid
        )
    )

    # Final calculations before the array is converted DataFrame
    averageLinkLoadTime = timeCalc / countValid
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

# Calculates the Website Score
print(maxTime, minTime)
for row in masterSiteData:
    A = (float(row[2]) - minTime) / (maxTime - minTime)
    B = float(row[3]) / (float(row[3]) + float(row[4]))
    row.append((A + B) / 2)

# Transforms the array to FataFrame. Makes it easier to save to a CSV file
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

# Sorts the siteData by the Website Score
masterSiteData = masterSiteData.sort_values(by=["Website Score"])

# Saves to CSV
masterLoadData.to_csv(
    "loadData.csv",
    index=False,
)
masterSiteData.to_csv(
    "siteData.csv",
    index=False,
)