from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
import time

# *** needed for soup
import requests

URL = "https://bing.campuscardcenter.com/ch/login.html"
page = requests.get(URL)

print(page.text)

# *** works better with Firefox, doesnt need the time.sleep to keep it open, doesnt crash when lines 16 & 17 are't commented
browser = webdriver.Chrome()

browser.get('https://bing.campuscardcenter.com/ch/login.html')

# *** no clue what this does 
#assert 'Youtube' in browser.title


# *** we'll probably use these to enter the username and password 
elem = browser.find_element(By.NAME, 'username')  # Find the username box
elem.send_keys('Jsearle1')  # enter username

elem = browser.find_element(By.NAME, 'password')  # Find the password box
elem.send_keys('Kayman123456' + Keys.RETURN)   # enter password then press return 


# *** selenium automatically closes the browser after the last line of code is executed apparently. 
# *** this was keeping it open for some reason 
time.sleep(100)

