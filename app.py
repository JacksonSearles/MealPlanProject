from flask import Flask, render_template, redirect, url_for, request, abort
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
import time

app = Flask(__name__, template_folder='templates')

@app.route('/')
def login():
	return render_template('index.html')

@app.route('/error')
def error():
	return render_template('error.html')


@app.route('/logged_in', methods = ['POST', 'GET'])
def logged_in():
	if request.method == 'POST' :
		username = request.form.get('username')
		password = request.form.get('password')
	
	options = webdriver.ChromeOptions()
	options.add_argument("--headless")

	browser = webdriver.Chrome(options=options)
	browser.get('https://bing.campuscardcenter.com/ch/login.html')

	# *** no clue what this does 
	#assert 'Youtube' in browser.title

	# *** we'll probably use these to enter the username and password 
	elem = browser.find_element(By.NAME, 'username')  # Find the username box
	elem.send_keys(username)  # enter username

	elem = browser.find_element(By.NAME, 'password')  # Find the password box
	elem.send_keys(password + Keys.RETURN)   # enter password then press return 

	if browser.find_element(By.ID, 'welcome') :
		return render_template('userPage.html', username=username)
	else:
		abort(400)
	

	
if __name__ == "__main__" :
	app.run(debug=True)



	
	

