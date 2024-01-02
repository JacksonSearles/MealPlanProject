from flask import Flask, render_template, redirect, url_for, request, session, flash
from py.mealplan import return_mealplan_data
from py.food import return_food_data
import json

######################################################################################################
# Defines the flask app as "app", and defines the /home route of website, which is the initial route 
# that runs when the app is first started. This function launches the login.html page, which is our 
# initial login page shown to the user.
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'binghamtonMealPlanApp'
@app.route('/')
@app.route('/home')
def home():
    if session.get('logged_in'):
        session.pop('logged_in', None)
    return render_template('login.html')
######################################################################################################

######################################################################################################
# Defines the /login route of website, which runs when the user clicks login button on our login page.
# If user is sucessfully logged in, they will be redirected to the /mealplan_tracker route, which 
# displays all information regarding their mealplan. If not sucessful, user is redirected backed to 
# /home route, which is our login page.
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']
    mealplan_data_filename = return_mealplan_data(username, password)
    food_data_filename = return_food_data()
    if mealplan_data_filename and food_data_filename: 
        session['logged_in'] = True
        return redirect(url_for('mealplan', mealplan_data_filename=mealplan_data_filename))
    else:
        flash('Incorrect username or password', 'danger')
        return redirect(url_for('home'))       
######################################################################################################

######################################################################################################
@app.route('/mealplan')
def mealplan(): 
    if session.get('logged_in'):
        view = request.args.get('view', 'mealplan')
        with open(f"{request.args.get('mealplan_data_filename', None)}", 'r') as file:
            mealplan_data = json.load(file)
        first_name = mealplan_data.get('first_name')
        mealplan_name = mealplan_data.get('mealplan_name')
        mealplan_balance = mealplan_data.get('mealplan_balance')
        days_left = mealplan_data.get('days_left')
        daily_budget = mealplan_data.get('daily_budget')
        funds_added = mealplan_data.get('funds_added')

        with open(f"{mealplan_data.get('transactions_filename')}", 'r') as file:
            transactions = json.load(file)
        with open(f"{mealplan_data.get('totals_by_date_filename')}", 'r') as file:
            totals_by_date = json.load(file)
        with open(f"{mealplan_data.get('graph_filename')}", 'r', encoding='utf-8') as file:
            graph_html = file.read()
            
        return render_template('loggedIn.html', first_name=first_name, mealplan_name=mealplan_name, mealplan_balance=mealplan_balance,
                    days_left=days_left, daily_budget=daily_budget, funds_added=funds_added, transactions=transactions,
                    totals_by_date=totals_by_date, graph_html=graph_html, view=view) 
    else:
        flash('You are not logged in. Please login to continue.', 'error')
        return redirect(url_for('home'))
######################################################################################################
    
######################################################################################################
#Defines the /food route, which runs when user clicks the "Food" button on navbar at the top of page. 
@app.route('/food')
def food():
    if session.get('logged_in'):
        view = request.args.get('view', None)
        with open(f"{request.args.get('mealplan_data_filename', None)}", 'r') as file:
            mealplan_data = json.load(file)
        first_name = mealplan_data.get('first_name')
        return render_template('loggedIn.html', first_name=first_name, view=view)
    else:
        flash('You are not logged in. Please login to continue.', 'error')
        return redirect(url_for('home'))
######################################################################################################   

######################################################################################################
# Defines the /logout route of website, which runs when user clicks the 'Logout' button. This will
# redirect the user back to the login page and sign them out of their account.
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))
######################################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    