#This file will scrape and return current food items available at dining halls
import os
from bs4 import BeautifulSoup
from datetime import date
import requests
import fitz

def return_demo_food_data():
    return 'food'

def return_food_data():
    current_day = date.today().strftime('%A')
    get_c4_menu(current_day)
    get_c4_kosher_menu(current_day)
    get_hinman_menu(current_day)
    get_app_menu(current_day)
    get_ciw_menu(current_day)
    return 'food'

def get_c4_menu(current_day):
    weekdays = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
    weekends = {'Saturday', 'Sunday'}
    folder_path = os.path.join('static', 'imgs', 'c4')
    pdf_path = os.path.join(folder_path, 'c4.pdf')
    os.makedirs(folder_path, exist_ok=True)
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
                return None

def get_c4_kosher_menu(current_day):
    folder_path = os.path.join('static', 'imgs', 'c4-kosher')
    pdf_path = os.path.join(folder_path, 'c4-kosher.pdf')
    os.makedirs(folder_path, exist_ok=True)
    pdf_link = None

    soup = BeautifulSoup(requests.get('https://binghamton.sodexomyway.com/dining-near-me/kosher-korner').text, "html.parser")
    foodmenu_spans = soup.find('div', class_='rtf').find('div', style='color: rgb(0, 103, 71);').find_all('span')
    for foodmenu_span in foodmenu_spans:
        for link in foodmenu_span.find_all('a'):
            if current_day in link.text:
                pdf_link = 'https:' + link.get('href')
                break

    with open(pdf_path, 'wb') as file: file.write(requests.get(pdf_link).content)
    with fitz.open(pdf_path) as pdf:
        for page_number in range(pdf.page_count):
            page = pdf[page_number]
            image = page.get_pixmap()
            if page_number == 0:
                image.save(os.path.join(folder_path, 'c4_kosher_lunch.png'))
            elif page_number == 1:
                image.save(os.path.join(folder_path, 'c4_kosher_dinner.png'))

def get_hinman_menu(current_day):
    return None

def get_app_menu(current_day):
    return None

def get_ciw_menu(current_day):
    return None
