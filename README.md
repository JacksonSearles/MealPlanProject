
# Mealplan Tracker

An interactive HTML/Python website, created by our ACM Projects Division group, that improves on Binghamton Unviversity's Mealplan website. This site is a one-stop shop that gathers all imporant information regarding a students mealplan account. Allows Binghamton University students to login into their mealplan accounts, and/or redirect them to create a mealplan account if they have yet to. Once logged in, imporatant information regarding the students mealplan will be displayed in an easy-to-follow format. If you are not a BU Student, but wish to test the functionality of
the website, type "demo" in username field, leave the password field blank, and click login button.


## Website Link

[https://bingmealplanhelper.pythonanywhere.com](https://bingmealplanhelper.pythonanywhere.com)






## Contributors

* [Nicholas DeNobrega](https://www.linkedin.com/in/nickdeno/)
* [Jackson Searles](https://www.linkedin.com/in/jackson-searles/)
* [Samuel Montes](https://www.linkedin.com/in/samuelmontes2026/)
* [Samuel Buckler](https://www.linkedin.com/in/samuel-buckler-18998a259/)
* [Allen Domingo](https://www.linkedin.com/in/allen-m-domingo/)

Project Idea Proposed by [Josef Schindler](https://www.linkedin.com/in/josef-schindler/) (President of Binghamton ACM)
## Information Displayed

* Mealplan Type
* Mealplan Balance
* How Many Days Left in Current Semester
* Daily Budget (Based on Current Balance and Days Left of Semester)
* Total Funds Added (How Much Money Student Has Added)
* Redirect Link to Add Funds to Mealplan
* All Recent Transactions (Date, Location, Price)
* Daily Spending (Graph and Table Format)
* Budget Chart for Current Semester(Based on BU Dining Service Chart)
* Food Currently Served at Each Dining Hall (In development still)

## Libraries Used

* Selenium: Opens private incognito browser used for scraping data from mealplan site, workaround due to Binghamton Mealplan site having the ability to detect multiple logins in a short period of time

* BeautifulSoup: Used for scraping HTML code from websites launched in Selenium browser. I.E, how we scrape the balance and transactions from the Binghamton Mealplan site

* Flask: At a high level, Flask is how we pass the data scraped from mealplan site using BeautifulSoup into the HTML code to be displayed for the user. Flask allows us to run Python functions based on the current route/url of the website. For example, if the user is at https://bingmealplanhelper.pythonanywhere.com/mealplan, the function named "mealplan" in app.py will run. Overall, we use Flask to handle GET and POST methods made from website. POST allows us to send data from the HTML page to the Python file, such as the username and password entered on our login page. GET allows the website to request some sort of data. In a majority of the GET requests, we use Flask to return an html page with some data passed through using Flask's render_template function, and display this data on the html page using the Jinja templating engine.

* Plotly: Used to create an interactive graph that displays the users daily spending.