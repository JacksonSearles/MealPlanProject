from flask import Flask, render_template, redirect, url_for, request, abort, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from bs4 import BeautifulSoup
import time

meal_plan_balance = 0
days_left = 0
daily_budget = 0
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
    global meal_plan_balance 
    global days_left
    global daily_budget

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

    if request.method == "PUT":
        return redirect(url_for('login'))

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.get('https://bing.campuscardcenter.com/ch/login.html')

    elem = browser.find_element(By.NAME, 'username')
    elem.send_keys(username)
    elem = browser.find_element(By.NAME, 'password')
    elem.send_keys(password + Keys.RETURN)

    try:
        if browser.find_element(By.ID, 'welcome'):
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            target_strings = ["Resident Holding - Carryover", "BUCS", "Meal Plan C"]
            body_content = soup.find("body").get_text()

            positions = {target: body_content.find(target) for target in target_strings}
            sorted_targets = sorted(positions.keys(), key=lambda x: positions[x])
            order = [sorted_targets.index(target) for target in target_strings]

            elements = soup.find_all(align="right")
            i = 0
            for e in elements:
                e_string = str(e)
                if "$" in e_string:
                    sub1 = """<div align="right">"""
                    sub2 = "</div>"
                    idx1 = e_string.index(sub1)
                    idx2 = e_string.index(sub2)
                    result = e_string[idx1 + len(sub1) + 3: idx2]
                    if i == order[0] or i == order[2]:
                        meal_plan_balance += float(result)
                    i += 1

            calculate_daily_spending()
            return render_template('userPage.html', username=username, balance=meal_plan_balance, days=days_left, budget=daily_budget)
    except NoSuchElementException:
        return redirect(url_for('error'))

def calculate_daily_spending():
    global days_left
    global daily_budget
    curr_date = datetime.now() 
    if 8 <= curr_date.month <= 12:  
        end_date = datetime(curr_date.year, 12, 31)
    else:
        end_date = datetime(curr_date.year, 5, 31) 
    days_left = (end_date - curr_date).days + 1 
    daily_budget = meal_plan_balance / days_left

if __name__ == '__main__':
    app.debug = True
    app.run()
