
# Mealplan Tracker

An interactive HTML/Python website, created by our ACM Projects Division group, that improves on Binghamton Unviversity's Mealplan website. This site is a one-stop shop that gathers all imporant information regarding a students mealplan account. Allows Binghamton University students to login into their mealplan accounts, and/or redirect them to create a mealplan account if they have yet to. Once logged in, imporatant information regarding the students mealplan will be displayed in an easy-to-follow format. 


## Website Link

[https://binghamton-mealplan-calculator.onrender.com/](https://binghamton-mealplan-calculator.onrender.com/)






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
* All Recent Transactions (Date, Location, Price)
* Redirect Link to Add Funds to Mealplan

## Libraries Used

* Selenium: Opens private incognito browser used for scraping data from mealplan site, workaround due to Binghamton Mealplan site having the ability to detect multiple logins in a short period of time

* BeautifulSoup: Used for scraping HTML code from websites launched in Selenium browser. I.E, how we scrape the balance and transactions from the Binghamton Mealplan site

* Flask: Allows for data to be passed in from Python file to HTML, using methods such as POST, PUT, etc. This is how we pass the data scraped using BeautifulSoup into the HTML code to be displayed for the user