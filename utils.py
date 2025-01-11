import config
import math,constants,config
from typing import List
import time
import openai
import os
import random
import json
from config import screenshot_dir, user_experience

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    options = browserOptions()
    
    try:
        driver = webdriver.Firefox(options=options)
        driver.get("https://www.linkedin.com/")
        time.sleep(3)
        
        with open("linkedin_cookies.json", "r") as cookiesfile:
            cookies = json.load(cookiesfile)
            for cookie in cookies:
                cookie = {key: cookie[key] for key in cookie if key in ["name", "value", "domain", "path", "expiry", "secure"]}
                driver.add_cookie(cookie)
        
        driver.refresh()
        return driver
    except WebDriverException as e:
        print(f"Error in setting up the driver: {e}")
        driver.save_screenshot("/error_screenshots/driver_setup_error.png")
        raise  # Re-raise the exception after logging
    
def generate_urls():
    if not os.path.exists('data'):
        os.makedirs('data')
    try: 
        with open('data/urlData.txt', 'w', encoding="utf-8") as file:
            linkedin_job_links = LinkedinUrlGenerate().generateUrlLinks()
            for url in linkedin_job_links:
                file.write(url + "\n")
        prGreen("Urls are created successfully, now the bot will visit those urls.")
    except Exception as e:
        prRed(f"Couldn't generate URLs: {e}")
    
def retry_find_element(driver, by, value, retries=3, delay=1):
    """Retry finding an element if StaleElementReferenceException occurs."""
    for attempt in range(retries):
        try:
            element = driver.find_element(by, value)
            return element
        except StaleElementReferenceException:
            print(f"Stale element reference. Retrying {attempt + 1}/{retries}...")
            time.sleep(delay)
    raise Exception(f"Failed to locate element by {by} = {value} after {retries} retries.")

def get_job_properties(driver, count):
    job_properties = {
        "title": "",
        "company": "",
        "location": "",
        "workplace": "",
        "applications": ""
    }

    xpaths = [
        ("title", "//div[@role='main']//div//div//div//div//div//div//h1"),
        ("company", "/html/body/div[6]/div[3]/div[2]/div/div/main/div/div[1]/div/div[1]/div/div/div[1]/div[1]/div/div/a"),
        ("location", "/html/body/div[6]/div[3]/div[2]/div/div/main/div/div[1]/div/div[1]/div/div/div[1]/div[3]/div/span[1]"),
        ("workplace", "/html/body/div[6]/div[3]/div[2]/div/div/main/div/div[1]/div/div[1]/div/div/div[1]/div[4]/ul/li[1]/span/span[1]/span/span[1]"),
        ("applications", "/html/body/div[6]/div[3]/div[2]/div/div/main/div/div[1]/div/div[1]/div/div/div[1]/div[3]/div/span[5]")
    ]

    for prop, xpath in xpaths:
        try:
            job_properties[prop] = driver.find_element(By.XPATH, xpath).get_attribute("innerHTML").strip()
        except Exception as e:
            #utils.prYellow(f"Warning in getting job {prop}: {str(e)[:100]}")
            continue

    return f"{count} | {job_properties['title']} | {job_properties['company']} | {job_properties['location']} | {job_properties['workplace']} | {job_properties['applications']}"


def application_questions(driver):
    """
    Fill in initial application questions: email, country, and phone number.
    """
    try:
        # Email field
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.clear()
            email_input.send_keys(config.email)
            print("Email entered successfully.")
        except (NoSuchElementException, TimeoutException):
            print("Email input field not found. Skipping this field.")

        # Country dropdown
        try:
            country_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"option[value='urn:li:country:{config.country_code}']"))
            )
            country_dropdown.click()
            print("Country selected successfully.")
        except (NoSuchElementException, TimeoutException):
            print("Country dropdown not found. Skipping this field.")

        # Phone number field
        try:
            phone_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='tel']"))
            )
            phone_input.clear()
            phone_input.send_keys(config.phone_number)
            print("Phone number entered successfully.")
        except (NoSuchElementException, TimeoutException):
            print("Phone number input field not found. Skipping this field.")

        time.sleep(random.uniform(1, constants.botSpeed))
        return True
    except Exception as e:
        print(f"Error during application questions: {e}")
        driver.save_screenshot("application_questions_error.png")
        return False

def retry_find_elements(driver, by, value, retries=3, delay=1):
    """Retry finding elements if StaleElementReferenceException occurs."""
    for attempt in range(retries):
        try:
            elements = driver.find_elements(by, value)
            return elements
        except StaleElementReferenceException:
            print(f"Stale element reference. Retrying {attempt + 1}/{retries}...")
            time.sleep(delay)
    raise Exception(f"Failed to locate elements by {by} = {value} after {retries} retries.")


def prompt():
    # Generate experience details dynamically
    experience_details = "You have experience in the following areas:\n"
    for skill, details in user_experience.items():
        experience_details += f"- {skill}: {details['level']} level with approximately {details['years']} years of experience.\n"
    
    # Construct the final prompt
    return (
        f"You are answering questions based on the following structured background:\n{experience_details}"
        "When asked, 'How long do you have experience in [skill or area]?', provide only the number of years based on the details above, "
        "without additional text. If the experience duration is unknown or not specified, respond with 0. "
        "Answer the following question:"
    )


    


def browserOptions():
    options = Options()
    
    # Set the Firefox profile path
    options.set_preference('profile', config.firefox_profile_path)

    # Basic options to optimize and control the browser
    options.add_argument("--start-maximized")  # Start maximized if running in a GUI
    options.add_argument("--ignore-certificate-errors")  # Ignore certificate warnings
    options.add_argument('--no-sandbox')  # No sandbox mode for better compatibility
    options.add_argument("--disable-extensions")  # Disable browser extensions
    options.add_argument('--disable-gpu')  # Disable GPU for better stability in some systems
    options.add_argument("--disable-blink-features")  # Disable specific features
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid automation detection

    # Headless mode option, based on configuration
    if config.headless:
        options.add_argument("--headless")

    # Optional: Disable WebRTC if privacy or tracking is a concern
    options.set_preference("media.peerconnection.enabled", False)

    # Optional: Enable strict tracking protection
    options.set_preference("privacy.trackingprotection.enabled", True)
    
    # Optional: Reduce logs (especially useful in headless mode)
    options.log.level = "error"

    return options


def prRed(prt):
    print(f"\033[91m{prt}\033[00m")

def prGreen(prt):
    print(f"\033[92m{prt}\033[00m")

def prYellow(prt):
    print(f"\033[93m{prt}\033[00m")

def getUrlDataFile():
    urlData = ""
    try:
        file = open('data/urlData.txt', 'r')
        urlData = file.readlines()
    except FileNotFoundError:
        text = "FileNotFound:urlData.txt file is not found. Please run ./data folder exists and check config.py values of yours. Then run the bot again"
        prRed(text)
    return urlData

def jobsToPages(numOfJobs):
    number_of_pages = 1

    if (' ' in numOfJobs):
        spaceIndex = numOfJobs.index(' ')
        totalJobs = (numOfJobs[0:spaceIndex])
        totalJobs_int = int(totalJobs.replace(',', ''))
        number_of_pages = math.ceil(totalJobs_int/constants.jobsPerPage)
        if (number_of_pages > 40 ): number_of_pages = 40

    else:
        number_of_pages = int(numOfJobs)

    return number_of_pages

def urlToKeywords(url: str) -> List[str]:
    keywordUrl = url[url.index("keywords=")+9:]
    keyword = keywordUrl[0:keywordUrl.index("&") ] 
    locationUrl =  url[url.index("location=")+9:]
    location = locationUrl
    return [keyword,location]

def writeResults(text: str):
    timeStr = time.strftime("%Y%m%d")
    fileName = "Applied Jobs DATA - " +timeStr + ".txt"
    try:
        with open("data/" +fileName, encoding="utf-8" ) as file:
            lines = []
            for line in file:
                if "----" not in line:
                    lines.append(line)
                
        with open("data/" +fileName, 'w' ,encoding="utf-8") as f:
            f.write("---- Applied Jobs Data ---- created at: " +timeStr+ "\n" )
            f.write("---- Number | Job Title | Company | Location | Work Place | Posted Date | Applications | Result "   +"\n" )
            for line in lines: 
                f.write(line)
            f.write(text+ "\n")
            
    except:
        with open("data/" +fileName, 'w', encoding="utf-8") as f:
            f.write("---- Applied Jobs Data ---- created at: " +timeStr+ "\n" )
            f.write("---- Number | Job Title | Company | Location | Work Place | Posted Date | Applications | Result "   +"\n" )

            f.write(text+ "\n")

def printInfoMes(bot:str):
    prYellow("ℹ️ " +bot+ " is starting soon... ")
    
def save_screenshot_with_path(driver, filename):
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, filename)
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")


class LinkedinUrlGenerate:
    def generateUrlLinks(self):
        path = []
        for location in config.location:
            for keyword in config.keywords:
                    url = constants.linkJobUrl + "?f_AL=true" + self.jobType() + "&keywords="+ keyword + '&location=' + location
                    path.append(url)
        print (path)
        return path

    def checkJobLocation(self,job):
        jobLoc = "&location=" +job
        match job.casefold():
            case "asia":
                jobLoc += "&geoId=102393603"
            case "europe":
                jobLoc += "&geoId=100506914"
            case "northamerica":
                jobLoc += "&geoId=102221843&"
            case "southamerica":
                jobLoc +=  "&geoId=104514572"
            case "australia":
                jobLoc +=  "&geoId=101452733"
            case "africa":
                jobLoc += "&geoId=103537801"

        return jobLoc

    def jobExp(self):
        jobtExpArray = config.experienceLevels
        firstJobExp = jobtExpArray[0]
        jobExp = ""
        match firstJobExp:
            case "Internship":
                jobExp = "&f_E=1"
            case "Entry level":
                jobExp = "&f_E=2"
            case "Associate":
                jobExp = "&f_E=3"
            case "Mid-Senior level":
                jobExp = "&f_E=4"
            case "Director":
                jobExp = "&f_E=5"
            case "Executive":
                jobExp = "&f_E=6"
        for index in range (1,len(jobtExpArray)):
            match jobtExpArray[index]:
                case "Internship":
                    jobExp += "%2C1"
                case "Entry level":
                    jobExp +="%2C2"
                case "Associate":
                    jobExp +="%2C3"
                case "Mid-Senior level":
                    jobExp += "%2C4"
                case "Director":
                    jobExp += "%2C5"
                case "Executive":
                    jobExp  +="%2C6"

        return jobExp

    def datePosted(self):
        datePosted = ""
        match config.datePosted[0]:
            case "Any Time":
                datePosted = ""
            case "Past Month":
                datePosted = "&f_TPR=r2592000&"
            case "Past Week":
                datePosted = "&f_TPR=r604800&"
            case "Past 24 hours":
                datePosted = "&f_TPR=r86400&"
        return datePosted

    def jobType(self):
        jobTypeArray = config.jobType
        firstjobType = jobTypeArray[0]
        jobType = ""
        match firstjobType:
            case "Full-time":
                jobType = "&f_JT=F"
            case "Part-time":
                jobType = "&f_JT=P"
            case "Contract":
                jobType = "&f_JT=C"
            case "Temporary":
                jobType = "&f_JT=T"
            case "Volunteer":
                jobType = "&f_JT=V"
            case "Internship":
                jobType = "&f_JT=I"
            case "Other":
                jobType = "&f_JT=O"
        for index in range (1,len(jobTypeArray)):
            match jobTypeArray[index]:
                case "Full-time":
                    jobType += "%2CF"
                case "Part-time":
                    jobType +="%2CP"
                case "Contract":
                    jobType +="%2CC"
                case "Temporary":
                    jobType += "%2CT"
                case "Volunteer":
                    jobType += "%2CV"
                case "Intership":
                    jobType  +="%2CI"
                case "Other":
                    jobType  +="%2CO"
        jobType += "&"
        return jobType

    def remote(self):
        remoteArray = config.remote
        firstJobRemote = remoteArray[0]
        jobRemote = ""
        match firstJobRemote:
            case "On-site":
                jobRemote = "f_WT=1"
            case "Remote":
                jobRemote = "f_WT=2"
            case "Hybrid":
                jobRemote = "f_WT=3"
        for index in range (1,len(remoteArray)):
            match remoteArray[index]:
                case "On-site":
                    jobRemote += "%2C1"
                case "Remote":
                    jobRemote += "%2C2"
                case "Hybrid":
                    jobRemote += "%2C3"

        return jobRemote

    def salary(self):
        salary = ""
        match config.salary[0]:
            case "$40,000+":
                salary = "f_SB2=1&"
            case "$60,000+":
                salary = "f_SB2=2&"
            case "$80,000+":
                salary = "f_SB2=3&"
            case "$100,000+":
                salary = "f_SB2=4&"
            case "$120,000+":
                salary = "f_SB2=5&"
            case "$140,000+":
                salary = "f_SB2=6&"
            case "$160,000+":
                salary = "f_SB2=7&"    
            case "$180,000+":
                salary = "f_SB2=8&"    
            case "$200,000+":
                salary = "f_SB2=9&"                  
        return salary

    def sortBy(self):
        sortBy = ""
        match config.sort[0]:
            case "Recent":
                sortBy = "sortBy=DD"
            case "Relevent":
                sortBy = "sortBy=R"                
        return sortBy

    
