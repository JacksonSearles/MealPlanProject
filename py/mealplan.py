from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import date, timedelta
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import pandas as pd
import requests
import json
import os

######################################################################################################
# Definition for custom "Transaction" object, which stores a date, location, and price in each object. 
# When we scrape transactions off mealplan website, each transaction is stored in a Tranasction
# object.
class Transaction:
    def __init__(self, date, location, price):
        self.date = date
        self.location = location
        self.price = float(price)
######################################################################################################
        
######################################################################################################     
# Definition for serializing Transaction Object. Since Transaction object is not a default object, we 
# need to create a custom serializer if we want to write it to a json file.
class TransactionSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Transaction):
            return obj.__dict__
        return super().default(obj)
######################################################################################################
    
######################################################################################################
# Returns demo mealplan data for when users who are not BU students want to test functionality of the
# website. This demo function will try and open the files at the location where they are stored on
# hosted website (bingmealplanhelper.pythonanywhere.come). If there is a FileNotFound Error, that means 
# the user is running demo locally, so we must retrieve local file paths
def return_demo_mealplan_data():
    first_name = 'Demo'
    mealplan_name = 'Meal Plan C'
    mealplan_balance = 21.8
    current_semester = 'Fall 2023'
    days_left_semester = 0
    daily_budget = 21.8
    funds_added = 250.0
    try:
        with open('/home/bingmealplanhelper/demo_data/demo_transactions.json'): pass
        transactions_filename = '/home/bingmealplanhelper/demo_data/demo_transactions.json'
        daily_spending_filename = '/home/bingmealplanhelper/demo_data/demo_daily_spending.json'
        graph_filename = '/home/bingmealplanhelper/demo_data/demo_graph.html'
    except FileNotFoundError:
        transactions_filename = 'data\\demo_transactions.json'
        daily_spending_filename = 'data\\demo_daily_spending.json'
        graph_filename = 'data\\demo_graph.html'   
    return first_name, mealplan_name, mealplan_balance, current_semester, days_left_semester, daily_budget, funds_added, transactions_filename, daily_spending_filename, graph_filename
######################################################################################################

######################################################################################################
# Takes username and password from our login page. Launches Selenium browser using launch_selenium_browser, 
# with the url of the actual Binghamton mealplan site. The username and password variables are passed 
# into actual Binghamton mealplan site to attempt to login the user. If login failed, no data
# is scraped and nothing is returned. If the user was logged in succesfully, browser.find element will 
# return true, and the rest of the program will run. scrape_mealplan_data() will scrape the first name
# of the user, the name of the meaplan they are on, there mealplan balance, and the href link that shows
# all transactions. scrape_mealplan_transactions() takes this link, and scrapes all transactions.
# scrape_academic_calendar() will scrape the academic calendar site to find the start and end days of the
# semester, and calculate_daily_budget() will use these dates and the current mealpan balance to claculate
# the daily budget that the user could spend. calculate_daily_spending will take the transactions scraped
# with scrape_mealplan_transactions, and determine how much the user has spent each day. This is done by
# adding up all the transactions with the same date. Finally, create_spending_graph() will take the result
# of calculate_daily_spending, and display this data in a graph.
def return_mealplan_data(username, password):
    browser = launch_selenium_browser(username, password)
    try:
        browser.find_element(By.ID, 'welcome')
    except NoSuchElementException:
        browser.quit()
        return None
    first_name, mealplan_name, mealplan_balance, transactions_href = scrape_mealplan_data(browser)
    transactions = scrape_mealplan_transactions(transactions_href, browser)
    fall_start_day, fall_end_day, spring_start_day, spring_end_day = scrape_academic_calander()
    current_semester, days_left_semester = calculate_current_date(fall_start_day, fall_end_day, spring_start_day, spring_end_day)
    daily_budget = calculate_daily_budget(mealplan_balance, days_left_semester)
    daily_spending, funds_added = calculate_daily_spending(transactions)
    graph = create_spending_graph(daily_spending, current_semester, fall_start_day, fall_end_day, spring_start_day, spring_end_day)

    data_folder = 'data'
    os.makedirs(data_folder, exist_ok=True)
    transactions_filename = os.path.join(data_folder, 'transactions.json')
    daily_spending_filename = os.path.join(data_folder, 'daily_spending.json')
    graph_filename = os.path.join(data_folder, 'graph.html')
    with open(transactions_filename, 'w') as file: json.dump(transactions, file, cls=TransactionSerializer)
    with open(daily_spending_filename,  'w') as file: json.dump(daily_spending, file)
    with open(graph_filename, 'w', encoding='utf-8') as file: file.write(graph)
       
    return first_name, mealplan_name, mealplan_balance, current_semester, days_left_semester, daily_budget, funds_added, transactions_filename, daily_spending_filename, graph_filename
######################################################################################################

######################################################################################################
# This function uses Selenium to open a headless incognito browser with the url of actual Binghamton
# mealplan site. Then Takes username and password gathered from Flask POST method, and sends them to 
# actual Binghamton meaplan site using .seny_keys, which will attempt to login user.
def launch_selenium_browser(username, password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get('https://bing.campuscardcenter.com/ch/login.html')
    browser.find_element(By.NAME, 'username').send_keys(username)
    browser.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)
    return browser
######################################################################################################

######################################################################################################
# This function scrapes important data about to the users mealplan. First we scrapes the first name of 
# the user, and store in first_name. Then finds the table element that holds all mealplan accounts, and 
# finds all the tr elements in the table, where each tr element is a mealplan account row. This is stored 
# in mealplan_accounts. Then we loop through each account in mealplan_accounts, and search to see if 
# this mealplan account is one of the mealplans defined in mealplans[] array. If it isnt, we continue to 
# the next account. If it is, we store the name of the meal plan account in mealplan_name, the balance of 
# the account in mealplan_balance, and scrape the href that holds the link to the full transactions page 
# and store in transactions_href.
def scrape_mealplan_data(browser):
    soup = BeautifulSoup(browser.page_source, "html.parser")
    first_name = soup.label.text.split()[2]
    transactions_href = None
    mealplan_name = None
    mealplan_balance = None
    carryover_balance = None
    mealplan_accounts = soup.find('table', {'width': '500', 'border': '0'}).find_all('tr')
    mealplans = ['Meal Plan C', 'Resident Holding - Carryover'	, 'Off Campus Holding - Carryover', 'Meal Plan A', 'Meal Plan B', 'Meal Plan D', 
                 'Meal Plan E', 'Meal Plan F', 'The 25.00 Plan', 'Commuter Semester', 'Commuter Annual']
    for account in mealplan_accounts[3:]:
        for mealplan in mealplans:
            if account.find('td', string=mealplan):
                if mealplan == 'Resident Holding - Carryover' or mealplan == 'Off Campus Holding - Carryover':
                    carryover_balance = float(account.find('div', {'align': 'right'}).text.strip().replace('$', '').replace('  ', ''))
                    break
                else: 
                    transactions_href = account.find('a')['href']
                    mealplan_balance = float(account.find('div', {'align': 'right'}).text.strip().replace('$', '').replace('  ', ''))
                    mealplan_name = mealplan
                    break
        if mealplan_balance is not None and carryover_balance is not None:
            break
    if mealplan_balance is None: mealplan_balance = 0
    if carryover_balance is None: carryover_balance = 0       
    return first_name, mealplan_name,  mealplan_balance+carryover_balance, transactions_href
######################################################################################################

######################################################################################################
# Updates the Selenium browser to open transactions page. Since all transactions are split between 
# multiple pages, we loop through all pages to scrape every transaction. Initially sets the curr_page
# as 1. Then we scrape the total number of transaction pages and store in total_pages. Then, loop through 
# every page of transactions and scrape every transaction on the page using BeautifulSoup. For each
# transaction, we create a Transaction object and add the date, location, and price to the Transaction 
# object, and add that object to transactions[] array. This is done for all transactions on the current 
# page. Then, iterate to next page by updating Selenium browser with href for next page and repeat.
def scrape_mealplan_transactions(transactions_href, browser):
    browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    curr_page = 1
    total_pages = int(soup.find('td', align='center', colspan='7').get_text(strip=True).replace(">>>", '').split(' ')[1].split('/')[1]) 
    transactions = []
    while curr_page <= total_pages:      
        entry_rows = soup.find_all('tr', {'id': 'EntryRow'})
        for entry_row in entry_rows:
            date = entry_row.contents[3].text.strip()
            location = entry_row.contents[7].text.strip().replace('Dining', '')
            price = entry_row.contents[9].div.text.strip().replace('(', '').replace(')', '')
            #When funds are added to account, there is no location
            if len(location) == 0:
                #True when current transaction is funds being added to account
                if entry_row.contents[5].text.strip() == 'ADDVALUE':
                    location = "Added Funds"
                #True when current transaction is the intial funds added to account
                elif entry_row.contents[5].text.strip() == 'Adj_Credit':
                    location = "Initial Funds"
            transactions.append(Transaction(date, location, price))
        curr_page += 1
        browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}&page={curr_page}")
        soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.quit()
    return transactions
######################################################################################################

######################################################################################################
# This function scrapes the Binghamton University academic calander for the start and end dates 
# of both the fall and spring semesters. It looks for the specific text provided and searches for the 
# date corelated with in in the previous tables box. It then splits the text, only getting the day and 
# returns it as an int. If all dates were found when scraping, return exact dates found. If all dates 
# werent found, we hard code a rough estimate of opening and closing days. This is the worst case 
# scenario and is done to prevent the website from failing to run alltogether if all dates werent 
# found. Right now we are just using the explicit dates listed on academic calendar for Fall 
# 2023 - Spring 2024.
def scrape_academic_calander():
    url = 'https://www.binghamton.edu/academics/academic-calendar.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    fall_start_day_target = soup.find_all('td', text='New Student Move-in and Welcome Program')
    fall_end_day_target = soup.find_all('td', text='Residence halls close at 10 a.m.')
    spring_start_day_target = soup.find_all('td', text='Resident Halls Open for Returning Students at 9am')
    spring_end_day_target = soup.find_all('td', text='Residence halls close for non-seniors at 10 a.m.')
    if len(fall_start_day_target) >= 1:
        fall_start_day = fall_start_day_target[0].find_previous_sibling('td').text.split()[-1]
    if len(fall_end_day_target) >= 1:
        fall_end_day = fall_end_day_target[1].find_previous_sibling('td').text.split()[-1]
    if len(spring_start_day_target) >= 1:
        spring_start_day = spring_start_day_target[0].find_previous_sibling('td').text.split()[-1]
    if len(spring_end_day_target) >= 1:
        spring_end_day = spring_end_day_target[0].find_previous_sibling('td').text.split()[-1] 
    if fall_start_day.isdigit() and fall_end_day.isdigit() and spring_start_day.isdigit() and spring_end_day.isdigit():
        return int(fall_start_day), int(fall_end_day), int(spring_start_day), int(spring_end_day)
    else:
        return 19, 16, 14, 10
######################################################################################################
    
######################################################################################################
# This function determines the current semester the user is in, and the days left in the current 
# semester based on start and end days scraped from the academic calendar
def calculate_current_date(fall_start_day, fall_end_day, spring_start_day, spring_end_day):
    current_semester = None 
    days_left_semester = 0
    curr_year = date.today().year
    curr_date = date.today()
    end_date = date.today()
    if date(curr_year, 8, fall_start_day) <= curr_date <= date(curr_year, 12, fall_end_day):
        end_date = date(curr_year, 12, fall_end_day)
        current_semester = f'Fall {curr_year}'
    elif date(curr_year, 1, spring_start_day) <= curr_date <= date(curr_year, 5, spring_end_day):
        end_date = date(curr_year, 5, spring_end_day)
        current_semester = f'Spring {curr_year}'
    elif (curr_date.month == 12 and date(curr_year, 12, fall_end_day) <= curr_date <= date(curr_year+1, 1, spring_start_day)) or curr_date.month == 1 and date(curr_year-1, 12, fall_end_day) <= curr_date <= date(curr_year, 1, spring_start_day):
        current_semester =  f'Spring {curr_year}'
    else:
        current_semester =  f'Summer {curr_year}'
    days_left_semester = (end_date - curr_date).days
    return current_semester, days_left_semester
######################################################################################################

######################################################################################################
# Takes in scraped meaplan balance and the days left in the semester, and calculates the daily 
# budget that person can spend until end of semeseter.
def calculate_daily_budget(meal_plan_balance, days_left_semester):
    return round((meal_plan_balance / days_left_semester), 2) if days_left_semester > 0 else meal_plan_balance
######################################################################################################

######################################################################################################
# Function that calculates the total amount spent for given dates, and  determines how much money has 
# additionally been added to account.First loops through each transaction in transactions[] array. For 
# each transaction, we check if the location is "Initial Funds". Since this is the original money on 
# mealplan account, we dont consider this for total spent. We also check if location of transaction is 
# "Added Funds". In this case, we dont consider this transaction for total spent because money was 
# added to account, not spent, however we do add this amount to funds_added to keep track of how much
# money was added. If neither of these cases are true, we check if the current transaction's date is 
# in the dictionary already. If it isnt, we add it to the dictionary. Finally, we add the the current
# transactions price to its corresponding date into the dictionary, and move on to next transaction.
# Finally, the total for each day is rounded to 2 decimal places.
def calculate_daily_spending(transactions):
    funds_added = 0
    daily_spending_dict = {}
    for transaction in transactions:
        if transaction.location == "Initial Funds":
            continue 
        elif transaction.location == "Added Funds":
            funds_added += transaction.price
        else:
            if transaction.date not in daily_spending_dict:
                daily_spending_dict[transaction.date] = 0
            daily_spending_dict[transaction.date] += transaction.price
    daily_spending_dict = {date: round(total, 2) for date, total in daily_spending_dict.items()}
    return daily_spending_dict, round(funds_added, 2)
######################################################################################################

######################################################################################################
# This function creates an interactive graph out of the users recent transactions. Accepts 
# total_spent_dict returned from the calculate_total_spent_daily function. The dict is turned into a 
# Pandas DataFrame consisting of a column of Dates and a column of Price (amount spent on that date).
# A Plotly Bar object is created out of the data from the DataFrame. A Plotly Layout object is created, 
# customizing the appearance of the graph. A Plotly Figure is created out of the Bar and Layout object.
# The Figure is then returned as an HTML string to be displayed on the website
def create_spending_graph(daily_spending_dict, current_semester,fall_end_day, spring_end_day, fall_start_day, spring_start_day):
    #CREATES PANDAS DATAFRAME OUT OF INPUT DICT, THEN SORTS DATES IN CHRONOLOGICAL ORDER
    df = pd.DataFrame(list(daily_spending_dict.items()), columns=['Date', 'Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)

    #CREATES DROPDOWN MENU FOR RANGE SELECTION
    curr_year = date.today().year
    dropdown_options = [
        {'label': 'Last 7 Days', 'method': 'relayout', 'args': [{'xaxis.range': [date.today() - timedelta(days=7), date.today()]}]},
        {'label': 'Last 14 Days', 'method': 'relayout', 'args': [{'xaxis.range': [date.today() - timedelta(days=14), date.today()]}]},
        {'label': 'Last 30 Days', 'method': 'relayout', 'args': [{'xaxis.range': [date.today() - timedelta(days=30), date.today()]}]},
    ]
    if 'Fall' in current_semester:
        dropdown_options.append({'label': 'Entire Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 8, fall_start_day), date(curr_year, 12, fall_end_day)]}]})
    elif 'Spring' in current_semester: 
        dropdown_options.append({'label': 'Entire Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]}]})

    #DESIGN LAYOUT OF GRAPH      
    hover_text = [f"{date.strftime('%b %d, %Y')}<br>Spent: ${price}" for date, price in zip(df['Date'], df['Price'])]
    bar = go.Bar(x=df['Date'], y=df['Price'], text=hover_text, hoverinfo='text', textposition="none", marker_color='#006747')
    layout = go.Layout(
        xaxis=dict(title_font=dict(size=30), type='date', showgrid=True, tickformat='%b %Y',tickfont=dict(size=15), range=[date.today() - timedelta(days=7), date.today()]),
        yaxis=dict(tickprefix='$', tickfont=dict(size=15, family="Arial Black, sans-serif"), range=[0, 10], autorange=True),
        hovermode='x',
        template='plotly_dark',
        paper_bgcolor='white',
        plot_bgcolor='white',   
        font=dict(color='black', family='Arial, sans-serif'),
        modebar_remove=['zoom', 'resetScale2d', 'pan', 'select2d', 'lasso', 'zoomIn', 'zoomOut', 'autoScale'],
        dragmode=False,
        margin=dict(l=0,r=0,t=10,b=0),
        updatemenus=[dict(
            buttons=dropdown_options, 
            direction="down", 
            pad={"r": 10, "t": 10}, 
            showactive=False,
            x=0.49, 
            xanchor="center", 
            y=1.2, 
            yanchor="top",
            bgcolor='#006747',  
            bordercolor='white',  
            font=dict(size=15, family='Arial, sans-serif', color='white'),
        )],     
    )
    fig = go.Figure(data=[bar], layout=layout)
    # plotly has no option to change the hover affect of its buttons. so this changes hover color of graph buttons (super jank fix but it works)
    return fig.to_html(fig, full_html=False).replace('activeColor:"#F4FAFF"', 'activeColor:"#006747"').replace('hoverColor:"#F4FAFF"', 'hoverColor:"grey"')             
######################################################################################################