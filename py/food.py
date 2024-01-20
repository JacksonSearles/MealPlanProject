#This script is run on a daily basis on the hosted site. I.E, it is not called in the program.
import os
from bs4 import BeautifulSoup
from datetime import date
import requests
import fitz

def get_c4_menu():
    weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
    weekends = {'Saturday', 'Sunday'}
    current_day = date.today().strftime('%A')
    folder_path = '/home/bingmealplanhelper/MealPlanProject/static/food_menus/c4'
    pdf_path = os.path.join(folder_path, 'c4.pdf')
    pdf_link = None
    
    soup = BeautifulSoup(requests.get('https://binghamton.sodexomyway.com/dining-near-me/c4-dining-hall').text, "html.parser")
    foodmenu_divs = soup.find('div', class_='rtf').find_all('div')
    for foodmenu_div in foodmenu_divs:
        for link in foodmenu_div.find_all('a'):
            if current_day in link.text:
                pdf_link = 'https:' + link.get('href')
                break
        if pdf_link:
            break

    with open(pdf_path, 'wb') as file: file.write(requests.get(pdf_link).content)
    with fitz.open(pdf_path) as pdf:
        for page_number in range(pdf.page_count):
            page = pdf[page_number]
            image = page.get_pixmap()
            if current_day in weekdays:
                if os.path.exists(os.path.join(folder_path, 'c4_simple_servings_breakfest.png')):
                    os.remove(os.path.join(folder_path, 'c4_simple_servings_breakfest.png'))
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'c4_breakfest.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'c4_lunch.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'c4_dinner.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'c4_simple_servings.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'c4_grill.png'))
                elif page_number == 5:
                    image.save(os.path.join(folder_path, 'c4_pizza.png'))
                elif page_number == 6:
                    image.save(os.path.join(folder_path, 'c4_expedition.png'))
            elif current_day in weekends:
                if os.path.exists(os.path.join(folder_path, 'c4_breakfest.png')):
                    os.remove(os.path.join(folder_path, 'c4_breakfest.png'))
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'c4_lunch.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'c4_dinner.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'c4_simple_servings_breakfest.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'c4_simple_servings.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'c4_grill.png'))
                elif page_number == 5:
                    image.save(os.path.join(folder_path, 'c4_pizza.png'))
                elif page_number == 6:
                    image.save(os.path.join(folder_path, 'c4_expedition.png'))


def get_c4_kosher_menu():
    days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Sunday'}
    current_day = date.today().strftime('%A')
    folder_path = '/home/bingmealplanhelper/MealPlanProject/static/food_menus/c4-kosher'
    pdf_path = os.path.join(folder_path, 'c4-kosher.pdf')
    pdf_link = None

    soup = BeautifulSoup(requests.get('https://binghamton.sodexomyway.com/dining-near-me/kosher-korner').text, "html.parser")
    foodmenu_spans = soup.find('div', class_='rtf').find('div', style='color: rgb(0, 103, 71);').find_all('span')
    for foodmenu_span in foodmenu_spans:
        for link in foodmenu_span.find_all('a'):
            if current_day in link.text:
                pdf_link = 'https:' + link.get('href')
                break
            if pdf_link:
                break
    if pdf_link is None: return

    with open(pdf_path, 'wb') as file: file.write(requests.get(pdf_link).content)
    with fitz.open(pdf_path) as pdf:
        for page_number in range(pdf.page_count):
            page = pdf[page_number]
            image = page.get_pixmap()
            if current_day in days:
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'c4_kosher_lunch.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'c4_kosher_dinner.png'))
            elif current_day == 'Friday':
                if os.path.exists(os.path.join(folder_path, 'c4_kosher_dinner.png')):
                    os.remove(os.path.join(folder_path, 'c4_kosher_dinner.png'))
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'c4_kosher_lunch.png'))
                  


def get_hinman_menu():
    weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
    weekends = {'Saturday', 'Sunday'}
    current_day = date.today().strftime('%A')
    folder_path = '/home/bingmealplanhelper/MealPlanProject/static/food_menus/hinman'
    pdf_path = os.path.join(folder_path, 'hinman.pdf')
    pdf_link = None

    soup = BeautifulSoup(requests.get('https://binghamton.sodexomyway.com/dining-near-me/hinman-dining-hall').text, "html.parser")
    foodmenu_divs = soup.find('div', class_='rtf').find_all('div')
    for foodmenu_div in foodmenu_divs:
        for link in foodmenu_div.find_all('a'):
            if current_day in link.text:
                pdf_link = 'https:' + link.get('href')
                break
        if pdf_link:
            break
    if pdf_link is None: return
    
    with open(pdf_path, 'wb') as file: file.write(requests.get(pdf_link).content)
    with fitz.open(pdf_path) as pdf:
        for page_number in range(pdf.page_count):
            page = pdf[page_number]
            image = page.get_pixmap()
            if current_day in weekdays:
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'hinman_breakfest.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'hinman_lunch.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'hinman_dinner.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'hinman_grill.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'hinman_garden_grill.png'))
                elif page_number == 5:
                    image.save(os.path.join(folder_path, 'hinman_pizza.png'))
                elif page_number == 6:
                    image.save(os.path.join(folder_path, 'hinman_expedition.png'))
            elif current_day in weekends:
                if os.path.exists(os.path.join(folder_path, 'hinman_breakfest.png')):
                    os.remove(os.path.join(folder_path, 'hinman_breakfest.png'))
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'hinman_lunch.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'hinman_dinner.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'hinman_grill.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'hinman_garden_grill.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'hinman_pizza.png'))
                elif page_number == 5:
                    image.save(os.path.join(folder_path, 'hinman_expedition.png'))


def get_app_menu():
    weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
    weekends = {'Saturday', 'Sunday'}
    current_day = date.today().strftime('%A')
    folder_path = '/home/bingmealplanhelper/MealPlanProject/static/food_menus/appalachian'
    pdf_path = os.path.join(folder_path, 'app.pdf')
    pdf_link = None

    soup = BeautifulSoup(requests.get('https://binghamton.sodexomyway.com/dining-near-me/appalachian-dining-hall').text, "html.parser")
    foodmenu_divs = soup.find('div', class_='rtf').find_all('div')
    for foodmenu_div in foodmenu_divs:
        for link in foodmenu_div.find_all('a'):
            if current_day in link.text:
                pdf_link = 'https:' + link.get('href')
                break
        if pdf_link:
            break
    if pdf_link is None: return
    
    with open(pdf_path, 'wb') as file: file.write(requests.get(pdf_link).content)
    with fitz.open(pdf_path) as pdf:
        for page_number in range(pdf.page_count):
            page = pdf[page_number]
            image = page.get_pixmap()
            if current_day in weekdays:
                if os.path.exists(os.path.join(folder_path, 'app_simple_servings_breakfest.png')):
                    os.remove(os.path.join(folder_path, 'app_simple_servings_breakfest.png'))
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'app_breakfest.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'app_lunch.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'app_dinner.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'app_simple_servings.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'app_grill.png'))
                elif page_number == 5:
                    image.save(os.path.join(folder_path, 'app_pizza.png'))
                elif page_number == 6:
                    image.save(os.path.join(folder_path, 'app_special_soup.png'))
            elif current_day in weekends:
                if os.path.exists(os.path.join(folder_path, 'app_breakfest.png')):
                    os.remove(os.path.join(folder_path, 'app_breakfest.png'))  
                elif page_number == 0:
                    image.save(os.path.join(folder_path, 'app_lunch.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'app_dinner.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'app_simple_servings_breakfest.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'app_simple_servings.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'app_grill.png'))
                elif page_number == 5:
                    image.save(os.path.join(folder_path, 'app_pizza.png'))
                elif page_number == 6:
                    image.save(os.path.join(folder_path, 'app_special_soup.png'))
                  

def get_ciw_menu():
    weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
    current_day = date.today().strftime('%A')
    folder_path = '/home/bingmealplanhelper/MealPlanProject/static/food_menus/ciw'
    pdf_path = os.path.join(folder_path, 'ciw.pdf')
    pdf_link = None

    soup = BeautifulSoup(requests.get('https://binghamton.sodexomyway.com/dining-near-me/college-in-the-woods-dining-hall').text, "html.parser")
    foodmenu_divs = soup.find('div', class_='rtf').find_all('div')
    for foodmenu_div in foodmenu_divs:
        for link in foodmenu_div.find_all('a'):
            if current_day in link.text:
                pdf_link = 'https:' + link.get('href')
                break
        if pdf_link:
            break
    if pdf_link is None: return
    
    with open(pdf_path, 'wb') as file: file.write(requests.get(pdf_link).content)
    with fitz.open(pdf_path) as pdf:
        for page_number in range(pdf.page_count):
            page = pdf[page_number]
            image = page.get_pixmap()
            if current_day != 'Friday' and current_day in weekdays:
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'ciw_breakfest.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'ciw_lunch.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'ciw_dinner.png'))
                elif page_number == 3:
                    image.save(os.path.join(folder_path, 'ciw_pizza.png'))
                elif page_number == 4:
                    image.save(os.path.join(folder_path, 'ciw_ultimate.png'))
            elif current_day == 'Friday':
                if os.path.exists(os.path.join(folder_path, 'ciw_dinner.png')):
                    os.remove(os.path.join(folder_path, 'ciw_dinner.png'))
                if os.path.exists(os.path.join(folder_path, 'ciw_ultimate.png')):
                    os.remove(os.path.join(folder_path, 'ciw_ultimate.png'))
                if page_number == 0:
                    image.save(os.path.join(folder_path, 'ciw_breakfest.png'))
                elif page_number == 1:
                    image.save(os.path.join(folder_path, 'ciw_lunch.png'))
                elif page_number == 2:
                    image.save(os.path.join(folder_path, 'ciw_pizza.png'))
            else:
                if os.path.exists(os.path.join(folder_path, 'ciw_breakfest.png')):
                    os.remove(os.path.join(folder_path, 'ciw_breakfest.png'))
                if os.path.exists(os.path.join(folder_path, 'ciw_lunch.png')):
                    os.remove(os.path.join(folder_path, 'ciw_lunch.png'))
                if os.path.exists(os.path.join(folder_path, 'ciw_dinner.png')):
                    os.remove(os.path.join(folder_path, 'ciw_dinner.png'))
                if os.path.exists(os.path.join(folder_path, 'ciw_pizza.png')):
                    os.remove(os.path.join(folder_path, 'ciw_pizza.png'))
                if os.path.exists(os.path.join(folder_path, 'ciw_pizza.png')):
                    os.remove(os.path.join(folder_path, 'ciw_pizza.png'))
                if os.path.exists(os.path.join(folder_path, 'ciw_ultimate.png')):
                    os.remove(os.path.join(folder_path, 'ciw_ultimate.png'))


get_c4_menu()
get_c4_kosher_menu()
get_hinman_menu()
get_app_menu()
get_ciw_menu()   