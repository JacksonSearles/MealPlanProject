import json
from datetime import datetime

######################################################################################################
# NOTE: THE PASSWORD OF THE USER IS NOT STORED, ONLY THEIR USERNAME AND FIRSTNAME.
# This function is used to log user interaction with the hosted website for statistical purposes. 
# This function checks if the user has logged in before by checking if their username is in the 
# website_users.json file. If it is, we increase the counter which keeps track of how many times they 
# have logged in, and log this message in website_interactions.txt. If this is their first time logging 
# into our site, their username is added to the website_users.json file and we display a message 
# in website_interactions.txt indicating this is their first time logging in. Also, when user logs out, 
# we display a message in website_interactions.txt indicating that they have logged out.
def log_website_interaction(username, first_name, action):
    date_time = datetime.now().strftime("%B %d, %Y: %I:%M %p")
    if action == 'login':
        with open('/home/bingmealplanhelper/demo_data/website_users.json', 'r') as file: 
            users = json.load(file)

        if username in users:
            users[username]['Number of Logins'] += 1
            log_message = f"{date_time}; {username} ({first_name}) has logged in for the {users[username]['Number of Logins']} time.\n"
        else:
            new_user = {
                'Username': username,
                'First Name': first_name,
                'First Login': date_time,
                'Number of Logins': 1    
            }
            users[username] = new_user
            log_message = f"{date_time}; {username} ({first_name}) logged in for the first time.\n"
            
        with open('/home/bingmealplanhelper/demo_data/website_users.json', 'r', 'w') as file: json.dump(users, file, indent=4)
        with open('/home/bingmealplanhelper/demo_data/website_interactions.txt', 'r', 'a') as file: file.write(log_message)

    elif action == 'logout':
        log_message = f"{date_time}; {username} ({first_name}) logged out.\n"
        with open('/home/bingmealplanhelper/demo_data/website_interactions.txt', 'a') as file: file.write(log_message)
######################################################################################################


