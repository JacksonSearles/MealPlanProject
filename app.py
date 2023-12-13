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
    dates, locations, prices = scrape_recent_transactions(soup, browser)
    
    # Call calculate_average_spending and then print out the averages 
    # Just proof of concept. 
    # not printing the dates in order because theyre just dummy dates real ones will always be chronological
    totals_by_date = calculate_total_spent_daily()
    for date, total_spent in totals_by_date.items():
        print("Total spent on", f'{date}: ${total_spent}')

    return render_template('userPage.html', first_name=first_name, mealplan_balance=mealplan_balance,
                days_left=days_left, daily_budget=daily_budget, dates=dates, locations=locations, prices=prices)
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
    locations = []
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
    #stores each transactions date in dates[] array, location in locations[] array, and stores 
    #transaction price in prices[] array. Then, iterateso next page by updating 
    #Selenium browser with href for next page and repeats.
    while cur_page <= total_page:      
        entry_rows = soup.find_all('tr', {'id': 'EntryRow'})
        for entry_row in entry_rows:
            try:
                contents = entry_row.contents
                date = contents[3].text.strip()
                location = contents[7].text.strip()
                #This condition occurs when money is added to mealplan, 
                #so its skipped
                if not location:
                    continue
                price = contents[9].div.text.strip().replace('(', '').replace(')', '')
                dates.append(date)
                locations.append(location)
                prices.append(price)
            except NoSuchElementException:
                print("Element not found. Check the HTML structure.")
        cur_page += 1
        browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}&page={cur_page}")
        soup = BeautifulSoup(browser.page_source, "html.parser")
    return dates, locations, prices
    #########################################################################

#########################################################################
# Function that calculates the total amount spent for given dates. 
# Loops through given 'dates' array and parses out just the date into new 'just_dates' array
# Creates a Pandas DataFrame made up of 'just_dates' and 'prices'. Basically conjoining the two original arrays
# Loops through the dates and sums up their spending 
# Adds the total and its date to the 'total_spent_dict' dictionary
# Returns 'total_spent_dict'
def calculate_total_spent_daily():
    # dummy arrays, just delete these and pass in the real ones
   # !!! will run into problems if the length of dates and prices dont match... is that possible?
    dates =  ['Jul 1st, 2023:', 'Jul 1st, 2023', 'Jul 1st, 2023', 'Jul 8th, 2023', 'Jul 8th, 2023', 'Jul 10th, 2023', 'Jul 11th, 2023', 'Jul 11th, 2023', 'Jul 12th, 2023', 'Jul 14th, 2023', 'Jul 15th, 2023', 'Jul 15th, 2023', 'Jul 15th, 2023', 'Jul 1st, 2099', 'Jul 1st, 2203', 'Jul 1st, 2303', 'Jul 1st, 2203', 'Jul 1st, 2213', 'Oct 10th, 2023', 'Oct 10th, 2023', 'Oct 10th, 2023']
    prices = [12.42, 10.99, 7, 11.33, 3, 18, 15.25, 12.42, 10.99, 7, 11.33, 3, 18, 150.25, 111, 99, 777, .01, 11.11, 99.82, .01]

    # Sets how many dates' averages you want to get 
    totals_to_find = 90
    
    # Creating a dictionary with the dates and prices arrays as the keys
    data = {'Date': dates, 'Price': prices}
    # Creating a Pandas DataFrame using the 'data' dictionary
    df = pd.DataFrame(data)

    # Creating a dictionary to store total spent on each date
    total_spent_dict = {}

    # Creating a counter to keep track of how many dates we've gone over
    totals_counter = 0
    # Iterate through unique dates and calculate total spent per day
    for unique_date in df['Date'].unique():
        # df[df['Date'] == unique_date] -> Filters the DataFrame so it is only rows with the a Date column equal to the 'unique_date' variable
        # ['Price'].sum()           -> Looks at the price column of the newly filtered DataFrame, and sums up the column
        total_spent = round(df[df['Date'] == unique_date]['Price'].sum(), 2)
        # Adds total_spent to the corresponding unique_date in the dict
        total_spent_dict[unique_date] = total_spent
        
        # Increment the counter and check to see if we've found the needed amount of totals
        totals_counter+=1
        if totals_counter == totals_to_find:
            break

    # Return the dict with the totals and their corresponding dates
    return total_spent_dict
#########################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)