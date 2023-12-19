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

##############################################################
#Creates a 'Transaction' object, which holds a date, location,
#and price. This object is used when scraping transactions from
#mealplan site
class Transaction:
    def __init__(self, date, location, price):
        self.date = date
        self.location = location
        self.price = float(price)
##############################################################

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
    transactions = scrape_mealplan_transactions(transactions_href, browser)
    days_left, daily_budget = calculate_daily_spending(mealplan_balance)
    totals_by_date, funds_added = calculate_total_spent_daily(transactions)
    fall_end_day, spring_end_day, fall_start_day, spring_start_day = academic_calander()
    graph_html = create_spending_graph(totals_by_date, fall_end_day, spring_end_day, fall_start_day, spring_start_day)
    return render_template('userPage.html', first_name=first_name, mealplan_name=mealplan_name, mealplan_balance=mealplan_balance,
                transactions=transactions, days_left=days_left, daily_budget=daily_budget, funds_added = funds_added, graph_html = graph_html, totals_by_date=totals_by_date)
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
    browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    page_numbers = soup.find('td', align='center', colspan='7').get_text(strip=True).replace(">>>", '').split(' ')[1].split('/')
    cur_page = int(page_numbers[0])
    total_page = int(page_numbers[1])  
    ##########################################################################
    
    ##########################################################################
    #Loops through every page of transactions using curr_page and total_page 
    #which were scraped earlier. Scrapes transactions page using BeautifulSoup, 
    #creates a Transaction object and adds the date, location, and price to the
    #Transaction object, and adds that object to transactions[] array, Then, 
    #iterate to next page by updating Selenium browser with href for next page 
    #and repeat.
    transactions = []
    while cur_page <= total_page:      
        entry_rows = soup.find_all('tr', {'id': 'EntryRow'})
        for entry_row in entry_rows:
            date = entry_row.contents[3].text.strip()
            location = entry_row.contents[7].text.strip().replace('Dining', '')
            price = entry_row.contents[9].div.text.strip().replace('(', '').replace(')', '')
            transactions.append(Transaction(date, location if location else "Added Funds", price))
        cur_page += 1
        browser.get(f"https://bing.campuscardcenter.com/ch/{transactions_href}&page={cur_page}")
        soup = BeautifulSoup(browser.page_source, "html.parser")
    return transactions
    #########################################################################

#########################################################################
#Takes in scraped meaplan balance, and calculates the daily budget
#that person can spend until end of semeseter
def calculate_daily_spending(meal_plan_balance):
    fall_end_day, spring_end_day,fall_start_day, spring_start_day = academic_calander()
    curr_date = date.today()
    end_date = date.today()
    year = curr_date.year
    if date(year, 8, fall_start_day) <= curr_date <= date(year, 12, fall_end_day):
        end_date = date(year, 12, fall_end_day)
    elif date(year, 1, spring_start_day) <= curr_date <= date(year, 5, spring_end_day):
        end_date = date(year, 5, spring_end_day)

    days_left = (end_date - curr_date).days
    if days_left > 0:
        daily_budget = round((meal_plan_balance / days_left), 2)
    else:
        daily_budget = meal_plan_balance
        days_left = 0
    return days_left, daily_budget
#########################################################################

######################################################################################################
# This function scrapes the Binghamton University academic calander for the end and start dates 
# of both the fall and spring semesters. It looks for the specific text provided and searches for the 
#date corelated with in in the previous tables box. It then splits the text, only getting the day and 
#returns it as an int
def academic_calander():
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
###############################################################################################

#############################################################################
# Function that calculates the total amount spent for given dates. 
# Creates a dictionary total_spent_dict. Within the dictionary, it will have
# a key:value pair of date:total_spent. First loops through each transaction
# in transactions[] array. For each transaction, we check if the location is 
# "Added Funds". In this case, we dont consider this transaction because money
# was added to account, not spent, so we use "continue" to skip this transaction
# . Then we check if the current transaction's date is in the dictionary already. 
# If it isnt, we add it to the dictionary. Finally, we add the the current 
# transactions price to its corresponding date into the dictionary, and move on
# to next transaction.
def calculate_total_spent_daily(transactions):
    fundsAdded = 0
    isFirstAddedFundsTransaction = True
    total_spent_dict = {}
    for transaction in transactions:
        if transaction.location == "Added Funds":
            if isFirstAddedFundsTransaction:
                isFirstAddedFundsTransaction = False
                continue  # Skip this transaction
            else:
                fundsAdded += transaction.price  # Add subsequent "Added Funds"
        else:
            if transaction.date not in total_spent_dict:
                total_spent_dict[transaction.date] = 0
            total_spent_dict[transaction.date] += transaction.price

    # Round the totals for each day
    total_spent_dict = {date: round(total, 2) for date, total in total_spent_dict.items()}
    return total_spent_dict, round(fundsAdded, 2)
##########################################################################

##########################################################################
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

    # Create hover box text
    hover_text = [f"{date.strftime('%b %d, %Y')}<br>Spent: ${price}" for date, price in zip(df['Date'], df['Price'])]

    # Create the bar graph data
    bar = go.Bar(x=df['Date'], y=df['Price'], text=hover_text, hoverinfo='text', textposition="none", marker_color='#006747')

    # !!! can get rid of this if we want
    year = date.today().year

    rangebuttons = [                                      
                
                # if in fall semester -> [date(year, 8, fall_start_day), date(year+1, 5, spring_end_day)] works well

                # if in spring semester, dates need to be:
                    # start dates = last years start dates
                    # end dates = current years end dates
            dict(label="School Year", method="relayout", args=[{"xaxis.range": [date(year, 8, fall_start_day), date(year+1, 5, spring_end_day)]}]),

                # if in fall semester -> [date(year, 8, fall_start_day), date(year, 12, fall_end_day)] works well

                # if in spring semester, dates need to be:
                    # start dates = last yeras start dates 
                    # end dates = last years end dates
            dict(label="Fall Semester", method="relayout", args=[{"xaxis.range": [date(year, 8, fall_start_day), date(year, 12, fall_end_day)]}]),

                # maybe dont show this button if youre in the fall semester? 
            dict(label="Spring Semester", method="relayout", args=[{"xaxis.range": [date(year, 12, spring_start_day), date(year, 12, spring_end_day)]}]),

                # good
            dict(label="Month", method="relayout", args=[{"xaxis.range": [date.today() - timedelta(days=30), date.today()]  } ]),
    ]

    # Create the layout of the graph
    layout = go.Layout(
        xaxis=dict(
            title="<b>Date</b>",
            title_font=dict(size=30),
            type='date', 
            showgrid=True,  
            tickformat='%b %Y',
            tickfont=dict(size=15),
        ),
        yaxis=dict(
            title='<b>Total Spent</b>', 
            title_font=dict(size=30), 
            tickprefix='$', 
            tickfont=dict(size=15, family="Arial Black, sans-serif")
        ),
        hovermode='x',
        template='plotly_dark',
        paper_bgcolor='white',
        plot_bgcolor='white',   
        font=dict(color='black', family='Arial, sans-serif'),
        updatemenus=[
            dict(type="buttons", direction="right", x=0.7, y=1.2, showactive=False, buttons=rangebuttons)    # <----- buttons 
        ] 
    )

    # Create the graph out of the bar data and layout
    fig = go.Figure(data=[bar], layout=layout)
    fig.update_layout(
        modebar_remove=['zoom', 'resetScale2d', 'pan', 'select2d', 'lasso', 'zoomIn', 'zoomOut', 'autoScale'],
        margin=dict(l=0,r=0,t=10,b=5))
    return fig.to_html(fig, full_html=False)           
##########################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)