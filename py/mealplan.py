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
        return Exception 
    first_name, mealplan_name, mealplan_balance, transactions_href = scrape_mealplan_data(browser)
    transactions = scrape_mealplan_transactions(transactions_href, browser)
    fall_start_day, fall_end_day, spring_start_day, spring_end_day = scrape_academic_calander()
    days_left, daily_budget = calculate_daily_budget(mealplan_balance, fall_start_day, fall_end_day, spring_start_day, spring_end_day)
    totals_by_date, funds_added = calculate_daily_spending(transactions)
    graph_html = create_spending_graph(totals_by_date, fall_start_day, fall_end_day, spring_start_day, spring_end_day)

    data_folder = 'data'
    os.makedirs(data_folder, exist_ok=True)
    transactions_filename = os.path.join(data_folder, 'transactions_filename.json')
    totals_by_date_filename = os.path.join(data_folder, 'totals_by_date_filename.json')
    graph_filename = os.path.join(data_folder, 'graph_file.html')
    mealplan_data_filename = os.path.join(data_folder, 'mealplan_data.json')
    mealplan_data = {
        'first_name': first_name,
        'mealplan_name': mealplan_name,
        'mealplan_balance': mealplan_balance,
        'days_left': days_left,
        'daily_budget': daily_budget,
        'funds_added': funds_added,
        'transactions_filename': transactions_filename,
        'totals_by_date_filename': totals_by_date_filename,
        'graph_filename': graph_filename,
    }

    with open(transactions_filename, 'w') as file:
        json.dump(transactions, file, cls=TransactionSerializer)
    with open(totals_by_date_filename,  'w') as file:
        json.dump(totals_by_date, file)
    with open(graph_filename, 'w', encoding='utf-8') as file:
        file.write(graph_html)   
    with open(mealplan_data_filename, 'w', encoding='utf-8') as file:
        json.dump(mealplan_data, file)

    return mealplan_data_filename
######################################################################################################

######################################################################################################
# This function uses Selenium to open a headless incognito browser with the url of actual Binghamton
# mealplan site. Then Takes username and password gathered from Flask POST method, and sends them to 
# actual Binghamton meaplan site using .seny_keys, which will attempt to login user.
def launch_selenium_browser(username, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(options=options)
    browser.get('https://bing.campuscardcenter.com/ch/login.html')

    elem = browser.find_element(By.NAME, 'username')
    elem.send_keys(username)
    elem = browser.find_element(By.NAME, 'password')
    elem.send_keys(password + Keys.RETURN)
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
    mealplan_accounts = soup.find('table', {'width': '500', 'border': '0'}).find_all('tr')
    mealplans = ['Meal Plan A', 'Meal Plan B', 'Meal Plan C', 'Meal Plan D', 'Meal Plan E', 'Meal Plan F',
                'The 25.00 Plan', 'Commuter Semester', 'Commuter Annual', 'Off Campus Holding - Carryover']
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
    dorms_open_fall = soup.find_all('td', text='New Student Move-in and Welcome Program')
    dorms_closed_fall = soup.find_all('td', text='Residence halls close at 10 a.m.')
    dorm_open_spring = soup.find_all('td', text='Resident Halls Open for Returning Students at 9am')
    dorms_closed_spring = soup.find_all('td', text='Residence halls close for non-seniors at 10 a.m.')

    if len(dorms_open_fall) >= 1:
        start_of_fall_semester = dorms_open_fall[0]
        dorm_open_date_fall = start_of_fall_semester.find_previous_sibling('td')
        full_date_fall_open = dorm_open_date_fall.text.split()
        fall_start_day = full_date_fall_open[-1]

    if len(dorms_closed_fall) >= 1:
        end_of_fall_semester = dorms_closed_fall[1]
        fall_date = end_of_fall_semester.find_previous_sibling('td')
        full_date_fall = fall_date.text.split()
        fall_end_day = full_date_fall[-1]

    if len(dorm_open_spring) >= 1:
        start_of_spring_semester = dorm_open_spring[0]
        dorm_open_date_spring = start_of_spring_semester.find_previous_sibling('td')
        full_date_spring_open = dorm_open_date_spring.text.split()
        spring_start_day = full_date_spring_open[-1]

    if len(dorms_closed_spring) >= 1:
        end_of_spring_semester = dorms_closed_spring[0]
        spring_date = end_of_spring_semester.find_previous_sibling('td')
        full_date_spring = spring_date.text.split()
        spring_end_day = full_date_spring[-1]
    
    if fall_start_day.isdigit() and fall_end_day.isdigit() and spring_start_day.isdigit() and spring_end_day.isdigit():
        return int(fall_start_day), int(fall_end_day), int(spring_start_day), int(spring_end_day)
    else:
        return 19, 16, 14, 10
######################################################################################################

######################################################################################################
# Takes in scraped meaplan balance, and calculates the daily budget that person can spend until end of 
# semeseter. Calculation is based on how many days there between the current day and the end
# of semester day.
def calculate_daily_budget(meal_plan_balance, fall_end_day, spring_end_day, fall_start_day, spring_start_day):
    curr_date = date.today()
    end_date = date.today()
    curr_year = curr_date.year
    if date(curr_year, 8, fall_start_day) <= curr_date <= date(curr_year, 12, fall_end_day):
        end_date = date(curr_year, 12, fall_end_day)
    elif date(curr_year, 1, spring_start_day) <= curr_date <= date(curr_year, 5, spring_end_day):
        end_date = date(curr_year, 5, spring_end_day)

    days_left = (end_date - curr_date).days
    if days_left > 0:
        daily_budget = round((meal_plan_balance / days_left), 2)
    else:
        daily_budget = meal_plan_balance
        days_left = 0
    return days_left, daily_budget
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
    total_spent_dict = {}
    for transaction in transactions:
        if transaction.location == "Initial Funds":
            continue 
        elif transaction.location == "Added Funds":
            funds_added += transaction.price
        else:
            if transaction.date not in total_spent_dict:
                total_spent_dict[transaction.date] = 0
            total_spent_dict[transaction.date] += transaction.price
    total_spent_dict = {date: round(total, 2) for date, total in total_spent_dict.items()}
    return total_spent_dict, round(funds_added, 2)
######################################################################################################

######################################################################################################
# This function creates an interactive graph out of the users recent transactions. Accepts 
# total_spent_dict returned from the calculate_total_spent_daily function. The dict is turned into a 
# Pandas DataFrame consisting of a column of Dates and a column of Price (amount spent on that date).
# A Plotly Bar object is created out of the data from the DataFrame. A Plotly Layout object is created, 
# customizing the appearance of the graph. A Plotly Figure is created out of the Bar and Layout object.
# The Figure is then returned as an HTML string to be displayed on the website
def create_spending_graph(total_spent_dict, fall_end_day, spring_end_day, fall_start_day, spring_start_day):
    #CREATES PANDAS DATAFRAME OUT OF INPUT DICT, THEN SORTS DATES IN CHRONOLOGICAL ORDER
    df = pd.DataFrame(list(total_spent_dict.items()), columns=['Date', 'Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    
    #CREATES DROPDOWN MENU FOR RANGE SELECTION
    curr_month = date.today().month
    curr_year = date.today().year
    dropdown_options = []
    # True when in fall semester
    if 8 <= curr_month <= 12:
        dropdown_options.extend([
            {'label': 'Current Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 8, fall_start_day), date(curr_year, 12, fall_end_day)]}]},
            {'label': 'Previous Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]}]},
            {'label': 'Current Month', 'method': 'relayout', 'args': [{'xaxis.range': [date.today() - timedelta(days=30), date.today()]}]},
            {'label': 'Current School Year', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 8, fall_start_day), date(curr_year+1, 5, spring_end_day)]}]}
        ])
        default_range = [date(curr_year, 8, fall_start_day), date(curr_year, 12, fall_end_day)]
    # True when in spring semester
    elif 1 <= curr_month <= 5:
        dropdown_options.extend([
            {'label': 'Current Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]}]},
            {'label': 'Previous Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year-1, 8, fall_start_day), date(curr_year-1, 12, fall_end_day)]}]},
            {'label': 'Current Month', 'method': 'relayout', 'args': [{'xaxis.range': [date.today() - timedelta(days=30), date.today()]}]},
            {'label': 'Current School Year', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year-1, 8, fall_start_day), date(curr_year, 5, spring_end_day)]}]}
        ])
        default_range = [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]
    #True when in the summer, only show most recent semester and most recent school year
    else:
        dropdown_options.extend([
            {'label': 'Most Recent Spring Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]}]},
            {'label': 'Most Recent School Year', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year-1, 8, fall_start_day), date(curr_year, 5, spring_end_day)]}]}
        ])
        default_range = [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]

    #DESIGN LAYOUT OF GRAPH      
    hover_text = [f"{date.strftime('%b %d, %Y')}<br>Spent: ${price}" for date, price in zip(df['Date'], df['Price'])]
    bar = go.Bar(x=df['Date'], y=df['Price'], text=hover_text, hoverinfo='text', textposition="none", marker_color='#006747')
    layout = go.Layout(
        xaxis=dict(
            title="<b>Date</b>",
            title_font=dict(size=30),
            type='date', 
            showgrid=True,  
            tickformat='%b %Y',
            tickfont=dict(size=15),
            range=default_range
        ),
        yaxis=dict( 
            tickprefix='$', 
            tickfont=dict(size=15, family="Arial Black, sans-serif")
        ),
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
        hovermode='x',
        template='plotly_dark',
        paper_bgcolor='white',
        plot_bgcolor='white',   
        font=dict(color='black', family='Arial, sans-serif'),
        modebar_remove=['zoom', 'resetScale2d', 'pan', 'select2d', 'lasso', 'zoomIn', 'zoomOut', 'autoScale'],
        margin=dict(l=0,r=0,t=10,b=0)    
    )
    fig = go.Figure(data=[bar], layout=layout)
    # plotly has no option to change the hover affect of its buttons. so this changes hover color of graph buttons (super jank fix but it works)
    return fig.to_html(fig, full_html=False).replace('activeColor:"#F4FAFF"', 'activeColor:"#006747"').replace('hoverColor:"#F4FAFF"', 'hoverColor:"grey"')             
######################################################################################################