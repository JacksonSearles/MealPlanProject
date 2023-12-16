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

#Selenium:      Opens private incognito browser used for scraping data from
#               mealplan site, workaround due to Binghamton Mealplan site
#               detecting multiple logins 

#Flask:         Allows for data to be passed in from Python file to HTML, using
#               methods such as POST, PUT, etc

#BeautifulSoup: Used for scraping HTML code from websites launched in
#               Selenium browser. I.E, how we scrape the balance and 
#               transactions from the Binghamton mealplan site

#Pandas:        Used to create a DataFrame of prices and dates. Uses the
#               DataFrame to calculate the total spent per date

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
    #Launches Selenium browser using launch_selenium_browser, with the url of the
    #Binghamton mealplan site. If the user was logged in succesfully, 
    #borwser.find element will return true, and the rest of the program will run.
    #If login failed, the user is prompted to login again. We use BeautifulSoup 
    #to get HTML code of Binghamton mealplan site. From this, we scrape the name of
    #the user, mealplan type, mealplan balance, and the link for the transactions page
    #with scrape_mealplan_data. Then we scrape all recent transaction prices and 
    #dates with scrape_recent_transactions. Then we calculate the daily budget based on 
    #balance using calculate_daily_spending, and also calculate the total spending
    #for each day using calculate_total_spent_daily. Finally, we launch the HTML 
    #landing page and pass values through using Flask render_template.    
    browser = launch_selenium_browser(username, password)
    try:
        browser.find_element(By.ID, 'welcome')
    except NoSuchElementException:
        return redirect(url_for('error'))
    first_name, mealplan_name, mealplan_balance, transactions_href = scrape_mealplan_data(browser)
    dates, locations, prices = scrape_mealplan_transactions(transactions_href, browser)
    days_left, daily_budget = calculate_daily_spending(mealplan_balance)
    totals_by_date = calculate_total_spent_daily(dates, prices)
    return render_template('userPage.html', first_name=first_name, mealplan_name=mealplan_name, mealplan_balance=mealplan_balance,
                dates=dates, locations=locations, prices=prices, days_left=days_left, daily_budget=daily_budget)
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

def scrape_mealplan_data(browser):
    ###########################################################################
    #Scrapes the first name of the user. Then finds the table element that holds 
    #all mealplan accounts(mealplan_accounts_table). Then finds all the tr elements
    #in the table, where each tr element is a mealplan account row, and store 
    #this in mealplan_accounts. Then we loop through each account in 
    #mealplan_accounts, and search to see if this mealplan account is one of 
    #the mealplans listed in mealplans[] array. If it isnt, we continue to the
    #next account. If it is, we store the name of the meal plan account found in
    #mealplan_name, then scrape the href that holds the link to the full 
    #transactions page and store in transactions_href, and scrape the balance of 
    #the account found and store in mealplan_balance.
    soup = BeautifulSoup(browser.page_source, "html.parser")
    first_name = soup.label.text.split()[2]
    transactions_href = None
    mealplan_name = None
    mealplan_balance = None
    mealplans = ['Meal Plan A', 'Meal Plan B', 'Meal Plan C', 'Meal Plan D', 'Meal Plan E', 'Meal Plan F',
                'The 25.00 Plan', 'Commuter Semester', 'Commuter Annual', 'Off Campus Holding - Carryover']
    mealplan_accounts_table = soup.find('table', {'width': '500', 'border': '0'})
    mealplan_accounts = mealplan_accounts_table.find_all('tr')
    for account in mealplan_accounts:
        for mealplan in mealplans:
            if account.find('td', string=mealplan):
                transactions_href = account.find('a')['href']
                mealplan_balance = float(account.find('div', {'align': 'right'}).text.strip().replace('$', '').replace('  ', ''))
                mealplan_name = mealplan
                break
        if transactions_href:
            break
    return first_name, mealplan_name, mealplan_balance, transactions_href
    ##########################################################################

def scrape_mealplan_transactions(transactions_href, browser):
    ##########################################################################
    #Updates the Selenium browser to open transactions page. Since all 
    #transactions are split between multiple pages, the current page and 
    #total page amounts are scraped and stored in page numbers[] array. 
    #This is so we can loop through all pages to scrape every transactions
    dates = []
    locations = []
    prices = []
    browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    page_numbers = soup.find('td', align='center', colspan='7').get_text(strip=True).replace(">>>", '').split(' ')[1].split('/')
    cur_page = int(page_numbers[0])
    total_page = int(page_numbers[1])  
    ##########################################################################
    
    ##########################################################################
    #Loops through every page of transactions using curr_page and total_page 
    #which were scraped earlier. Scrapes transactions page using BeautifulSoup, 
    #stores each transactions date in dates[] array, location in locations[] 
    #array, and stores transaction price in prices[] array. Then, iterate to 
    #next page by updating Selenium browser with href for next page and repeat.
    while cur_page <= total_page:      
        entry_rows = soup.find_all('tr', {'id': 'EntryRow'})
        for entry_row in entry_rows:
            try:
                contents = entry_row.contents
                date = contents[3].text.strip()
                location = contents[7].text.strip().replace('Dining', '')
                #This condition occurs when money is added to mealplan, 
                #so its skipped
                if not location:
                    continue
                price = contents[9].div.text.strip().replace('(', '').replace(')', '')
                dates.append(date)
                locations.append(location)
                prices.append(float(price))
            except NoSuchElementException:
                print("Element not found. Check the HTML structure.")
        cur_page += 1
        browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}&page={cur_page}")
        soup = BeautifulSoup(browser.page_source, "html.parser")
    return dates, locations, prices
    #########################################################################

def calculate_daily_spending(meal_plan_balance):
    #########################################################################
    #Takes in scraped meaplan balance, and calculates the daily budget
    #that person can spend until end of semeseter
    curr_date = datetime.now()
    if 8 <= curr_date.month <= 12:
        end_date = datetime(curr_date.year, 12, 16)
    else:
        end_date = datetime(curr_date.year, 5, 16)
    days_left = (end_date - curr_date).days + 1
    try:
        daily_budget = round((meal_plan_balance / days_left), 2)
    except ZeroDivisionError:
        daily_budget = meal_plan_balance
    return days_left, daily_budget
    #########################################################################

#############################################################################
# Function that calculates the total amount spent for given dates. 
# Creates a Pandas DataFrame made up of 'dates' and 'prices'. Basically 
# conjoining the two original arrays.Loops through the dates and sums up 
# their spending. Adds the total and its date to the 'total_spent_dict' 
# dictionary. Returns 'total_spent_dict'
def calculate_total_spent_daily(dates, prices):
    data = {'Date': dates, 'Price': prices}
    df = pd.DataFrame(data)
    total_spent_dict = {}
    for unique_date in df['Date'].unique():
        # df.groupby('Date')['Price'].sum(). --> Groups the DataFrame by 'Date' column and selects 'Price' column, calculates the sum for every date in the df 
        # loc[unique_date]                   --> uses .loc[unique_date] to only look at the 'unique_date's sum
        total_spent = round(df.groupby('Date')['Price'].sum().loc[unique_date], 2)
        total_spent_dict[unique_date] = total_spent
    return total_spent_dict
##########################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)