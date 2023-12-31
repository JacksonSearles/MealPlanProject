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
        #username = request.form['username']
        #password = request.form['password']
        username = 'ndenobrega'
        password = '21Velocity21@'
    try:
        mealplan_data = return_mealplan_data(username, password)
        food_data = return_food_data()
        session['logged_in'] = True
    except Exception:
        flash('Incorrect username or password', 'danger')
        return redirect(url_for('home'))       
    return redirect(url_for('mealplan', first_name=mealplan_data[0], mealplan_name=mealplan_data[1], mealplan_balance=mealplan_data[2], 
                days_left=mealplan_data[3], daily_budget=mealplan_data[4], funds_added=mealplan_data[5], recent_transaction_filename=mealplan_data[6], 
                totals_by_date_filename=mealplan_data[7], graph_filename=mealplan_data[8]))
######################################################################################################

######################################################################################################
@app.route('/mealplan')
def mealplan(): 
    if session.get('logged_in'):
        first_name = request.args.get('first_name', None)
        mealplan_name = request.args.get('mealplan_name', None)
        mealplan_balance = request.args.get('mealplan_balance', None)
        days_left = request.args.get('days_left', None)
        daily_budget = request.args.get('daily_budget', None)
        funds_added = request.args.get('funds_added', None)
    
        recent_transaction_filename = request.args.get('recent_transaction_filename')
        with open(recent_transaction_filename, 'r') as file:
            transactions = json.load(file)

        totals_by_date_filename = request.args.get('totals_by_date_filename')
        with open(totals_by_date_filename, 'r') as file:
            totals_by_date = json.load(file)

        graph_filename = request.args.get('graph_filename')
        with open(graph_filename, 'r', encoding='utf-8') as file:
            graph_html = file.read()
            
        view = request.args.get('view', 'mealplan')
        return render_template('loggedin.html', first_name=first_name, mealplan_name=mealplan_name, mealplan_balance=mealplan_balance,
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
    view = request.args.get('view', None)
    return render_template('loggedin.html', view=view)
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
    