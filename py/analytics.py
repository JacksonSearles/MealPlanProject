import json
from datetime import datetime

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



