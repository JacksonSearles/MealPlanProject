from flask import Flask, render_template, redirect, url_for, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

#Libraries Used: Flask, Selenium, BeautifulSoup, Pandas
#Selenium: Opens private incognito browser used for scraping data from
#          mealplan site, workaround due to Binghamton Mealplan site
#          detecting multiple logins 
#Flask: Allows for data to be passed in from Python file to HTML, using
#       methods such as POST, PUT, etc
#BeautifulSoup: Used for scraping HTML code from websites launched in
#               Selenium browser. I.E, how we scrape the balance and 
#               transactions from the Binghamton mealplan site
#Pandas:    Used to create a DataFrame of prices and dates. Uses the
#           DataFrame to calculate the average spent per date

app = Flask(__name__, template_folder='templates')

@app.route('/')
@app.route('/home')
def login():
    return render_template('index.html')

@app.route('/error')
def error():
    message = "Incorrect username or password"
    return render_template('index.html', message=message)

@app.route('/logged_in', methods=['POST', 'GET', 'PUT'])
def logged_in():
    #############################################################################
    #Takes username and password from login page and stores in username and 
    #password variables using Flask POST method
    if request.method == 'POST': 
        username = request.form.get('username')
        password = request.form.get('password')
    ##############################################################################

    ##############################################################################
    #Launches Selenium browser using launch_selenium_browser, and uses BeautifulSoup 
    #to get HTML code of Binghamton mealplan site. From this, we scrape the mealplan 
    #balance, all recent transaction pricesand dates, calculate the daily budget 
    #based on balance, and finally launch the HTML landing page and pass values 
    #through using Flask render_template.    
    browser = launch_selenium_browser(username, password)
    try:
        browser.find_element(By.ID, 'welcome')
    except NoSuchElementException:
        return redirect(url_for('error'))
    soup = BeautifulSoup(browser.page_source, "html.parser")
    first_name = soup.label.text.split()[2]
    mealplan_balance = scrape_mealplan_balance(soup)
    days_left, daily_budget = calculate_daily_spending(mealplan_balance)
    dates, prices = scrape_recent_transactions(soup, browser)
    
    # Call calculate_average_spending and then print out the averages 
    # Just proof of concept. 
    # not printing the dates in order because theyre just dummy dates real ones will always be chronological
    averages = calculate_average_spending()
    for date, average_spending in averages.items():
        print("Average spent on", f'{date}: ${average_spending}')

    return render_template('userPage.html', first_name=first_name, mealplan_balance=mealplan_balance,
                days_left=days_left, daily_budget=daily_budget, dates=dates, prices=prices)
    ############################################################################
    
def launch_selenium_browser(username, password):
    ###########################################################################
    #Selenium opens headless incognito browser withe the url of mealplan site
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(options=options)
    browser.get('https://bing.campuscardcenter.com/ch/login.html')
    ############################################################################

    ############################################################################
    #Takes username and password gathered from Flask POST method, 
    #and sends keys to actual mealplan Binghamton site to login user
    elem = browser.find_element(By.NAME, 'username')
    elem.send_keys(username)
    elem = browser.find_element(By.NAME, 'password')
    elem.send_keys(password + Keys.RETURN)
    ############################################################################
    return browser

def scrape_mealplan_balance(soup):
    ###########################################################################
    #Reason for Code: Website formats balances in different order for different 
    #people. so this determines order of mealplan balances for the user to 
    #determine location of relevant balances in HTML code
    target_strings = ["Resident Holding - Carryover", "BUCS", "Meal Plan C"]
    body_content = soup.find("body").get_text()
    positions = {target: body_content.find(target) for target in target_strings}
    sorted_targets = sorted(positions.keys(), key=lambda x: positions[x])
    order = [sorted_targets.index(target) for target in target_strings]
    elements = soup.find_all(align="right")
    ###########################################################################

    ###########################################################################
    #Iterates through selected elements, finds element with monetary amount($), 
    #isolates the balance, and adds to meal_plan_balance
    mealplan_balance = 0
    i = 0
    for e in elements:
        e_string = str(e)
        if "$" in e_string:
            sub1 = """<div align="right">"""
            sub2 = "</div>"
            idx1 = e_string.index(sub1)
            idx2 = e_string.index(sub2)
            result = e_string[idx1 + len(sub1) + 3: idx2]
            #This checks to see if the balance being scanned is the one 
            #we care about. If so, add the amount to mealplan_balance
            if i == order[0] or i == order[2]:
                mealplan_balance += float(result)
            i += 1
    ###########################################################################
    return mealplan_balance

###############################################################################
#Takes in scraped meaplan balance, and calculates the daily budget
#that person can spend until end of semeseter
def calculate_daily_spending(meal_plan_balance):
    curr_date = datetime.now()
    if 8 <= curr_date.month <= 12:
        end_date = datetime(curr_date.year, 12, 15)
    else:
        end_date = datetime(curr_date.year, 5, 15)
    days_left = (end_date - curr_date).days + 1
    daily_budget = round((meal_plan_balance / days_left), 2)
    return days_left, daily_budget
###############################################################################

def scrape_recent_transactions(soup, browser):
    dates = []
    prices = []
    ###########################################################################
    #Finds href link of the recent transactions page using BeautifulSoup, and 
    #updates the Selenium browser to open transactions page. Since all
    #transaction are split between multiple pages, the current page and total 
    #page amounts are scraped and stored in page numbers[] array. This is so we 
    #can loop through all pages to scrape every transactions
    transactions_href = soup.find('table', {'width': '500', 'border': '0'}).find('a', href=True).get('href', None)
    browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    page_numbers = soup.find('td', align='center', colspan='7').get_text(strip=True).replace(">>>", '').split(' ')[1].split('/')
    cur_page = int(page_numbers[0])
    total_page = int(page_numbers[1])  
    ##########################################################################
    
    ##########################################################################
    #Loops through every page of transactions using curr_page and total_page 
    #which were scraped earlier. Scrapes transactions page using BeautifulSoup, 
    #stores each transactions date and location in dates[] array and stores 
    #transaction price in prices array. Then, iterateso next page by updating 
    #Selenium browser with href for next page and repeats.
    while cur_page <= total_page:      
        entry_rows = soup.find_all('tr', {'id': 'EntryRow'})
        for entry_row in entry_rows:
            try:
                contents = entry_row.contents
                date = contents[3].text.strip()
                dining_hall = contents[7].text.strip()
                #This condition occurs when money is added to mealplan, 
                #so its skipped
                if not dining_hall:
                    continue
                price = contents[9].div.text.strip().replace('(', '').replace(')', '')
                dates.append(f"{date}: {dining_hall}")
                prices.append(f"${price}")
            except NoSuchElementException:
                print("Element not found. Check the HTML structure.")
        cur_page += 1
        browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}&page={cur_page}")
        soup = BeautifulSoup(browser.page_source, "html.parser")
    return dates, prices
    #########################################################################

#########################################################################
# !!! This is just grabbing all of the averages. not sure how to control how many actual dates were 

# Function that calculates average spending for given dates. 
# loops through given 'dates' array and parses out just the date into new 'just_dates' array
# Creates a Pandas DataFrame made up of 'just_dates' and 'prices'. Basically conjoining the two original arrays
# Loops through the dates and averages out their spending 
# Adds the average and its date to the 'average_spending_dict' dictionary
# returns 'average_spending_dict'
def calculate_average_spending():
    # dummy arrays, just delete these and pass in the real ones
   # !!! will run into problems if the length of dates and prices dont match... is that possible?
    dates =  ['Jul 1st, 2023: Hinman', 'Jul 1st, 2023: Hinman', 'Jul 1st, 2023: College in The Woods', 'Jul 8th, 2023: C4', 'Jul 8th, 2023: Hinman', 'Jul 10th, 2023: Hinman', 'Jul 11th, 2023: Hinman', 'Jul 11th, 2023: Hinman', 'Jul 12th, 2023: Hinman', 'Jul 14th, 2023: College in The Woods', 'Jul 15th, 2023: C4', 'Jul 15th, 2023: Hinman', 'Jul 15th, 2023: Hinman', 'Jul 1st, 2099: Hinman', 'Jul 1st, 2203: Hinman', 'Jul 1st, 2303: Hinman', 'Jul 1st, 2203: Hinman', 'Jul 1st, 2213: Hinman', 'Oct 10th, 2023: Hinman', 'Oct 10th, 2023: Hinman', 'Oct 10th, 2023: Hinman']
    prices = [12.42, 10.99, 7, 11.33, 3, 18, 15.25, 12.42, 10.99, 7, 11.33, 3, 18, 150.25, 111, 99, 777, .01, 11.11, 99.82, .01]

    # Will hold just the dates after they are spliced out of the 'dates' array
    just_dates = []

    # Sets how many dates' averages you want to get 
    averages_to_find = 90

   # !!! This loop just goes through all the dates. Even if averages_to_find = 2 and theres 100 dates, itll still go through all of them... not efficient 
   # !!! this might not be needed. might not even need a 'just_dates' array and just use the given 'dates' array and splice out the date as you go... idk
    # Loops through the dates array and pulls out just the dates, creating a new array of just_dates
    for element in dates:
        # Extract the date using string slicing
        date_part = element.split(":")[0].strip()
        # add the date to the just_dates array
        just_dates.append(date_part)
    
    # Creating a dictionary with the dates and prices arrays as the keys
    data = {'Date': just_dates, 'Price': prices}
    # Creating a Pandas DataFrame using the data dictionary
    df = pd.DataFrame(data)

    # Creating a dictionary to store average spending for each date
    average_spending_dict = {}

    # Creating a counter to keep track of how many dates we've gone over
    unique_dates_counter = 0
    # Iterate through unique dates and calculate average spending
    for unique_date in df['Date'].unique():
        # Only select the rows of the df with the given unique_date, then
        # selects 'price' column from df, then calculates mean of the prices, and then round it to 2 decimal places
        average_spending = round(df[df['Date'] == unique_date]['Price'].mean(), 2)
        # Adds average_spending to the corresponding unique_dates in the dict
        average_spending_dict[unique_date] = average_spending
        
        # Increment the counter and check to see if we've found the needed amount of averages
        unique_dates_counter+=1
        if unique_dates_counter >= averages_to_find:
            break

    # Return the dict with the averages and their corresponding dates
    return average_spending_dict
#########################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)