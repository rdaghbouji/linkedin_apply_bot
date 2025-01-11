# General bot settings

# Optional! run browser in headless mode, no browser screen will be shown it will work in background.
headless = False

firefox_profile_path = ""

# These settings are for running Linkedin job apply bot
LinkedinBotProPasswrod = ""
# location you want to search the jobs - ex : ["Poland", "Singapore", "New York City Metropolitan Area", "Monroe County"]
# continent locations:["Europe", "Asia", "Australia", "NorthAmerica", "SouthAmerica", "Africa", "Australia"]
location = [""]
# keywords related with your job search
keywords = ["" ]
# keywords = ["programming"]
#job experience Level - ex:  ["Internship", "Entry level" , "Associate" , "Mid-Senior level" , "Director" , "Executive"]
experienceLevels = ["" ]
#job posted date - ex: ["Any Time", "Past Month" , "Past Week" , "Past 24 hours"] - select only one
datePosted = [""]
# datePosted = ["Past 24 hours"]
#job type - ex:  ["Full-time", "Part-time" , "Contract" , "Temporary", "Volunteer", "Intership", "Other"]
jobType = [""]
#remote  - ex: ["On-site" , "Remote" , "Hybrid"]
remote = [""]
#salary - ex:["$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+" ] - select only one
salary = [""]
#sort - ex:["Recent"] or ["Relevent"] - select only one
sort = [""]
#Blacklist companies you dont want to apply - ex: ["Apple","Google"]
blacklist = [""]
#Blaclist keywords in title - ex:["manager", ".Net"]
blackListTitles = [""]
#Only Apply these companies -  ex: ["Apple","Google"] -  leave empty for all companies 
onlyApply = [""]
#Only Apply titles having these keywords -  ex:["web", "remote"] - leave empty for all companies 
onlyApplyTitles = [""] 
#Follow companies after sucessfull application True - yes, False - no
followCompanies = False
# your country code for the phone number - ex: fr
country_code = "fr"
# Your phone number without identifier - ex: 123456789
phone_number = ""

# Your experience will be used to generate custom prompt to handle application questions
user_experience = {
    "Skill or Domain 1": {"level": "Beginner", "years": 1},
    "Skill or Domain 2": {"level": "Intermediate", "years": 3},
    "Skill or Domain 3": {"level": "Advanced", "years": 5},
    "Skill or Domain 4": {"level": "Expert", "years": 7},
}


screenshot_dir = "./error_screenshots"
