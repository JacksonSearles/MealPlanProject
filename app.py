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

@app.route('/logged_in', methods = ['POST', 'GET', 'PUT'])
def logged_in():
	global meal_plan_balance 
	global days_left
	global daily_budget

	if request.method == 'POST' :
		username = request.form.get('username')
		password = request.form.get('password')

	if request.method == "PUT" :
		return redirect(url_for('login'))	
	
	options = webdriver.ChromeOptions()
	options.add_argument("--headless")
	browser = webdriver.Chrome(options=options)
	browser.get('https://bing.campuscardcenter.com/ch/login.html')
	elem = browser.find_element(By.NAME, 'username')  # Find the username box
	elem.send_keys(username)  # enter username then press return
	elem = browser.find_element(By.NAME, 'password')  # Find the password box
	elem.send_keys(password + Keys.RETURN)   # enter password then press return 
	message = username

	try :
		if browser.find_element(By.ID, 'welcome') :
			result = '0'
			html = browser.page_source
			soup = BeautifulSoup(html, "html.parser")
			elements = soup.find_all(align = "right")
			for e in elements:
				if "$" in str(e):
					e_string = str(e) 
					sub1 = """<div align="right">"""
					sub2 = "</div>"
					# getting index of substrings
					idx1 = e_string.index(sub1)
					idx2 = e_string.index(sub2)
					result = str(float(result) + float(e_string[idx1 + len(sub1) + 3: idx2]))
			meal_plan_balance = float(result)
			calculate_daily_spending()
			return render_template('userPage.html', username=username, message=message, balance = meal_plan_balance, 
						  days = days_left, budget = daily_budget)
	except NoSuchElementException : 
			return redirect(url_for('error'))
	
# Assuming balance will be passed in
def calculate_daily_spending():
	global days_left
	global daily_budget
	curr_date = datetime.now() 
	if 8 <= curr_date.month <= 12:  
		end_date = datetime(curr_date.year, 12, 31) # Fall semester
	else:
		end_date = datetime(curr_date.year, 5, 31) # Spring semester 
	days_left = (end_date - curr_date).days + 1 
	daily_budget = round(meal_plan_balance / days_left, 2)

if __name__ == '__main__':
    app.debug = True
    app.run()



	
	

