from flask import Flask, render_template, redirect, url_for, request, session, flash
from py.analytics import log_website_interaction
from py.mealplan import return_mealplan_data, return_demo_mealplan_data
from py.food import return_food_data, return_demo_food_data
import json

all_users = None
######################################################################################################
# Defines the Flask application as "app", and sets the location of the templates folder. The templates 
# folder contains the html files needed for website.
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'binghamtonMealPlanApp'
######################################################################################################

######################################################################################################
# Ensures that bingmealplanhelper.pythonanywhere.com (hosted site) will always run the function 
# connected to each route. Sometimes, the site will cache pages connected to a route, which prevents
# the function attached to route from running (speeds up performance). However, since some of our
# functions manually clear the session to prevent non-loggedin users from acessing certain routes 
# of the website, we disable this caching to prevent non-loggedin users from returning to routes
# meant for logged in users such as /mealplan and /food.
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response
######################################################################################################

######################################################################################################
# Defines the /home route of website, which is the initial route that runs when the app is first 
# started. This function checks if there is a current session where the user was already logged in,
# and clears the session if true. This is to prevent the user from being able to go back and forth 
# between the /home route and other routes in the website that should only be accessed after logging 
# in. I.E, once user returns to the /home route (login page), they are not aloud to go back other routes 
# in the website without relogging in. Then, the login.html page is launched, which is our initial login 
# page shown to the user.
@app.route('/')
@app.route('/home')
def home():
    if session.get("logged_in"):
        session.clear()
    return render_template('login.html')
######################################################################################################

######################################################################################################
# Defines the /login route of website, which runs when the user clicks login button on our login page.
# If user is sucessfully logged in, all mealplan data will be retrieved using get_mealplan_data, and 
# stored in the sites "session"/cookies. Also, the login status of the user will be stored in the 
# session. This status will be checked for each route of the website, which ensures non-logged in users
# arent able to access routes that should only be accessed after logging in. After this, the user will 
# be redirected to the /mealplan route, which displays all information regarding their mealplan. If 
# login was not sucessful, user is redirected back to /home route, which is our login page.
@app.route('/login', methods=['POST', 'GET'])
def login():
    mealplan_data = None  
    food_data = None
    if request.method == 'POST':
        if request.form['username'] == 'demo':
            mealplan_data = return_demo_mealplan_data()
            food_data = return_demo_food_data()
        else:
            username = request.form['username']
            password = request.form['password']
            mealplan_data = return_mealplan_data(username, password)
            food_data = return_food_data()
    if mealplan_data and food_data:
        session.update({
            'logged_in': True,
            'username': username,
            'first_name': mealplan_data[0],
            'mealplan_name': mealplan_data[1],
            'mealplan_balance': mealplan_data[2],
            'current_semester': mealplan_data[3],
            'days_left_semester': mealplan_data[4],
            'daily_budget': mealplan_data[5],
            'funds_added': mealplan_data[6],
            'transactions': mealplan_data[7],
            'daily_spending': mealplan_data[8],
            'graph': mealplan_data[9],
            #.....Data about food items at dining fall will be stored here aswell   
        })
        log_website_interaction(username, session.get('first_name'), 'login')
        return redirect(url_for('mealplan'))
    else:
        flash('Incorrect username or password', 'danger')
        return redirect(url_for('home'))       
######################################################################################################

######################################################################################################
# Defines the /mealplan route of website, which runs when the user first sucesfully signs in, or when 
# user clicks the "Mealplan" tab on navbar. The function for this route will first check if user is 
# logged in. This is to prevent user from acessing this page if not logged in, and will redirect them 
# back to /home route (login page) if they are not logged in. Then, all mealplan data is retrieved from 
# the current session, and then rendered on the page. NOTE: 'view' variable is used to keep track of 
# the which html page should be loaded onto the page. In this case, view = 'mealplan', so the the 
# loggedIn.html page will be rendered with the mealplan.html embedded inside of it.
@app.route('/mealplan')
def mealplan(): 
    if session.get('logged_in'):
        with open(f"{session.get('transactions')}", 'r') as file: transactions = json.load(file)
        with open(f"{session.get('daily_spending')}", 'r') as file: daily_spending = json.load(file)
        with open(f"{session.get('graph')}", 'r', encoding='utf-8') as file: graph = file.read()    
        return render_template('loggedIn.html', view='mealplan', first_name=session.get('first_name'), 
                mealplan_name=session.get('mealplan_name'), mealplan_balance=session.get('mealplan_balance'),
                current_semester=session.get('current_semester'),days_left_semester=session.get('days_left_semester'), 
                daily_budget=session.get('daily_budget'), funds_added=session.get('funds_added'), 
                transactions=transactions, daily_spending=daily_spending, graph=graph) 
    else:
        return redirect(url_for('home'))
######################################################################################################
    
######################################################################################################
# Defines the /bduget route of website, which runs when the user clicks the "How to Budget" tab on navbar. 
# The function for this route will first check if user is logged in. This is to prevent user from 
# acessing this page if not logged in, and will redirect them back to /home route (login page) if they 
# are not logged in. Then, the current semester is feteched from the current session. If the semester
# is Fall, the Fall Mealplan Budget Chart will be displayed, if semeseter is Spring the Spring Mealplan
# Budget Chart will be displayed, else no chart will be displayed. NOTE: 'view' variable is used to keep 
# track of the which html page should be loaded onto the page. In this case, view = 'budget', so the
# the loggedIn.html page will be rendered with the budget.html embedded inside of it.
@app.route('/budget')
def budget():
    if session.get('logged_in'):
        if 'Fall' in session.get('current_semester'):
            chart_title = 'Fall Budget Chart'
            current_semester = 'Fall'
        elif 'Spring' in session.get('current_semester'):
            chart_title = 'Spring Budget Chart'
            current_semester = 'Spring'
        else:
            chart_title = 'Budget Chart'
            current_semester = '' 
        return render_template('loggedIn.html', view='budget',
                first_name=session.get('first_name'), chart_title=chart_title,
                current_semester=current_semester)
    else:
        return redirect(url_for('home'))
######################################################################################################
    
######################################################################################################
# Defines the /food route of website, which runs when the user clicks the "Food" tab on navbar. 
# The function for this route will first check if user is logged in. This is to prevent user from 
# acessing this page if not logged in, and will redirect them back to /home route (login page) if they 
# are not logged in. Then, all food related data is retrieved from the current session, and then rendered 
# on the page. NOTE: 'view' variable is used to keep track of the which html page should be loaded onto 
# the page. In this case, view = 'food', so the the loggedIn.html page will be rendered with the 
# food.html embedded inside of it.
@app.route('/food')
def food():
    if session.get('logged_in'):
        return render_template('loggedIn.html', view='food', first_name=session.get('first_name'))
    else:
        return redirect(url_for('home'))
######################################################################################################   

######################################################################################################
# Defines the /logout route of website, which runs when user clicks the 'Logout' button. This will
# clear the current session (login status, meaplan data, etc), sign them out of their account, and
# redirect them back to the /home route (login page)
@app.route('/logout')
def logout():
    log_website_interaction(session.get('username'), session.get('first_name'), 'logout')
    session.clear()
    return redirect(url_for('home'))
######################################################################################################

######################################################################################################
# Launches Flask app.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
######################################################################################################    