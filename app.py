from flask import Flask, render_template, redirect, url_for, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from datetime import date, timedelta
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import pandas as pd
import requests

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

#Plotly:        Used to create an interactive graph of the users spending over time

class Transaction:
    def __init__(self, date, location, price):
        self.date = date
        self.location = location
        self.price = float(price)

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

#################################################################################
# Takes username and password from login page and stores in username and 
# password variables using Flask POST method
# Launches Selenium browser using launch_selenium_browser, with the url of the
# Binghamton mealplan site. If the user was logged in succesfully, 
# borwser.find element will return true, and the rest of the program will run.
# If login failed, the user is prompted to login again. We use BeautifulSoup 
# to get HTML code of Binghamton mealplan site. From this, we scrape the name of
# the user, mealplan type, mealplan balance, and the link for the transactions page
# with scrape_mealplan_data. Then we scrape all recent transaction prices and 
# dates with scrape_recent_transactions. Then we calculate the daily budget based on 
# balance using calculate_daily_spending, and also calculate the total spending
# for each day using calculate_total_spent_daily. Finally, we launch the HTML 
# landing page and pass values through using Flask render_template.  
def logged_in():
    if request.method == 'POST': 
        username = request.form.get('username')
        password = request.form.get('password')

    browser = launch_selenium_browser(username, password)
    try:
        browser.find_element(By.ID, 'welcome')
    except NoSuchElementException:
        return redirect(url_for('error'))
    first_name, mealplan_name, mealplan_balance, transactions_href = scrape_mealplan_data(browser)
    transactions = scrape_mealplan_transactions(transactions_href, browser)
    fall_end_day, spring_end_day, fall_start_day, spring_start_day = scrape_academic_calander()
    days_left, daily_budget = calculate_daily_spending(mealplan_balance, fall_end_day, spring_end_day, fall_start_day, spring_start_day)
    totals_by_date, funds_added = calculate_total_spent_daily(transactions)
    graph_html = create_spending_graph(totals_by_date, fall_end_day, spring_end_day, fall_start_day, spring_start_day)
    return render_template('userPage.html', first_name=first_name, mealplan_name=mealplan_name, mealplan_balance=mealplan_balance,
                transactions=transactions, days_left=days_left, daily_budget=daily_budget, funds_added = funds_added, graph_html = graph_html, totals_by_date=totals_by_date)
###############################################################################

###############################################################################
# Selenium opens headless incognito browser withe the url of mealplan site,
# Takes username and password gathered from Flask POST method, and sends keys 
# to actual mealplan Binghamton site to login user
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
###############################################################################

###############################################################################
# Scrapes the first name of the user. Then finds the table element that holds 
# all mealplan accounts(mealplan_accounts_table). Then finds all the tr elements
# in the table, where each tr element is a mealplan account row, and store 
# this in mealplan_accounts. Then we loop through each account in 
# mealplan_accounts, and search to see if this mealplan account is one of 
# the mealplans listed in mealplans[] array. If it isnt, we continue to the
# next account. If it is, we store the name of the meal plan account found in
# mealplan_name, then scrape the href that holds the link to the full 
# transactions page and store in transactions_href, and scrape the balance of 
# the account found and store in mealplan_balance.
def scrape_mealplan_data(browser):
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
#############################################################################

def scrape_mealplan_transactions(transactions_href, browser):
    #########################################################################
    # Updates the Selenium browser to open transactions page. Since all 
    # transactions are split between multiple pages, the current page and 
    # total page amounts are scraped and stored in page numbers[] array. 
    # This is so we can loop through all pages to scrape every transactions
    browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    page_numbers = soup.find('td', align='center', colspan='7').get_text(strip=True).replace(">>>", '').split(' ')[1].split('/')
    cur_page = int(page_numbers[0])
    total_page = int(page_numbers[1])  
    #########################################################################
    
    #########################################################################
    # Loops through every page of transactions using curr_page and total_page 
    # which were scraped earlier. Scrapes transactions page using BeautifulSoup, 
    # creates a Transaction object and adds the date, location, and price to the
    # Transaction object, and adds that object to transactions[] array, Then, 
    # iterate to next page by updating Selenium browser with href for next page 
    # and repeat.
    transactions = []
    while cur_page <= total_page:      
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
        cur_page += 1
        browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}&page={cur_page}")
        soup = BeautifulSoup(browser.page_source, "html.parser")
    return transactions
    #########################################################################

######################################################################################################
# This function scrapes the Binghamton University academic calander for the end and start dates 
# of both the fall and spring semesters. It looks for the specific text provided and searches for the 
# date corelated with in in the previous tables box. It then splits the text, only getting the day and 
# returns it as an int
def scrape_academic_calander():
    url = 'https://www.binghamton.edu/academics/academic-calendar.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    dorms_open_fall = soup.find_all('td', text='New Student Move-in and Welcome Program')
    dorm_open_spring = soup.find_all('td', text='Resident Halls Open for Returning Students at 9am')
    dorms_closed_fall = soup.find_all('td', text='Residence halls close at 10 a.m.')
    dorms_closed_spring = soup.find_all('td', text='Residence halls close for non-seniors at 10 a.m.')

    if len(dorms_closed_fall) >= 1:
        end_of_fall_semester = dorms_closed_fall[1]
        fall_date = end_of_fall_semester.find_previous_sibling('td')
        full_date_fall = fall_date.text.split()
        fall_end_day = full_date_fall[-1]

    if len(dorms_closed_spring) >= 1:
        end_of_spring_semester = dorms_closed_spring[0]
        spring_date = end_of_spring_semester.find_previous_sibling('td')
        full_date_spring = spring_date.text.split()
        spring_end_day = full_date_spring[-1]

    if len(dorms_open_fall) >= 1:
        start_of_fall_semester = dorms_open_fall[0]
        dorm_open_date_fall = start_of_fall_semester.find_previous_sibling('td')
        full_date_fall_open = dorm_open_date_fall.text.split()
        fall_start_day = full_date_fall_open[-1]

    if len(dorm_open_spring) >= 1:
        start_of_spring_semester = dorm_open_spring[0]
        dorm_open_date_spring = start_of_spring_semester.find_previous_sibling('td')
        full_date_spring_open = dorm_open_date_spring.text.split()
        spring_start_day = full_date_spring_open[-1]

    return int(fall_end_day), int(spring_end_day), int(fall_start_day), int(spring_start_day)
######################################################################################################

######################################################################################################
# Takes in scraped meaplan balance, and calculates the daily budget that person can spend until end of 
# semeseter. Calculation is based on the the how many days there between the current day and the end
# of semester day.
def calculate_daily_spending(meal_plan_balance, fall_end_day, spring_end_day, fall_start_day, spring_start_day):
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
def calculate_total_spent_daily(transactions):
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
# This function creates an interactive graph out of the users recent transactions.
# Accepts total_spent_dict from the calculate_total_spent_daily function.
# The dict is turned into a Pandas DataFrame consisting of a column of Dates and 
# a column of Price (amount spent on that date)
# A Plotly Bar object is created out of the data from the DataFrame
# A Plotly Layout object is created, customizing the appearance of the graph
# A Plotly Figure is created out of the Bar and Layout object
# The Figure is then returned as an HTML string to be displayed on the website
def create_spending_graph(total_spent_dict, fall_end_day, spring_end_day, fall_start_day, spring_start_day):
    # Create Pandas DataFrame out of input dict, then sort dates in chronological order
    df = pd.DataFrame(list(total_spent_dict.items()), columns=['Date', 'Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True)
    
    #CREATE DROPDOWN MENU FOR RANGE SELECTION
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
            {'label': 'Most Recent Semester', 'method': 'relayout', 'args': [{'xaxis.range': [date(curr_year, 1, spring_start_day), date(curr_year, 5, spring_end_day)]}]},
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
    graph_html = fig.to_html(fig, full_html=False)
    # plotly has no option to change the hover affect of its buttons. so this changes hover color of graph buttons (super jank fix but it works)
    graph_html = graph_html.replace('activeColor:"#F4FAFF"', 'activeColor:"#006747"').replace('hoverColor:"#F4FAFF"', 'hoverColor:"grey"')
    return graph_html              
######################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)