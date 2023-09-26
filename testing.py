from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
import time

# *** works better with Firefox, doesnt need the time.sleep to keep it open, doesnt crash when lines 16 & 17 are't commented
browser = webdriver.Chrome()

browser.get('https://bing.campuscardcenter.com/ch/login.html')

# *** no clue what this does 
#assert 'Youtube' in browser.title

# *** we'll probably use these to enter the username and password 
#elem = browser.find_element(By.NAME, 'p')  # Find the search box
#elem.send_keys('youtube' + Keys.RETURN)

# *** selenium automatically closes the browser after the last line of code is executed apparently. 
# *** this keeps it open for some reason 
time.sleep(1)

