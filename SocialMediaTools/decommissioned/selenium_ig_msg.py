from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located, presence_of_element_located
import time 
import datetime
import random 
import pyautogui
import json
import sys
import pandas as pd 

with open('title_dict.json') as f: 
    msg_dict = json.load(f)

if len(msg_dict) == 0:
    print("Database empty. Please parse more accounts")
    sys.exit()

k = 10 if len(msg_dict) >= 10 else len(msg_dict)

current_payload = dict(list(msg_dict.items())[:k])

users = list(current_payload.keys())
albums = list(current_payload.values())


for user in users:
    print(f"Song title for {user}: " + current_payload[user] + '\n')
    modified_title = input("Please enter modified title (type KEEP to keep current title): ")
    if modified_title == "KEEP":
        pass 
    elif modified_title == "SKIP":
        current_payload[user] = ""
    else:
        current_payload[user] = modified_title


PATH = "C:\\Program Files (x86)\\chromedriver.exe"
options = Options()
options.add_argument("user-data-dir=C:\\Users\\hansu\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 3")
options.add_argument("profile-directory=Profile 3")
driver = Chrome(executable_path=PATH, options=options)
driver.get('https://www.instagram.com/')

time.sleep(random.randint(3, 10))
try:
    not_now_notifs = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='aOOlW   HoLwm ']"))
    ).click()
except:
    pass

time.sleep(random.randint(3, 10))

counter = 0
database = pd.read_csv('testing.csv')
while counter < len(users):
    for user in users:
        driver.get(f'https://www.instagram.com/{user}')
        try:
            # Click "message" next to username
            follow_click = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='_5f5mN       jIbKX  _6VtSN     yZn4P   ']"))
            ).click()
            time.sleep(random.randint(5, 10))

            message_click = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='sqdOP  L3NKy    _8A5w5    ']"))
                ).click()
            time.sleep(random.randint(5, 10)) 

            # Find message bar
            message_bar = driver.find_element_by_xpath("//textarea[@class='focus-visible']")
            time.sleep(random.randint(5, 10))

            # Send message 

            if current_payload[user] == 'N/A':
                msg_string = "Your tracks go crazy bro frfr, u got potential keep going"
            elif current_payload[user] == "":
                msg_string = ""
            else:
                msg_string = f"Your music hard asf bro, been steady listening to {current_payload[user]}"

            # New
            del[msg_dict[list(msg_dict.keys())[0]]]

            time.sleep(random.randint(5, 10))
            message_bar.clear()
            message_bar.send_keys(msg_string)
            time.sleep(random.randint(5, 10))
            message_bar.send_keys(Keys.ENTER)
            print("Successfully sent message to {}!".format(user))
            time.sleep(random.randint(5, 10))
            counter += 1
        except:
            print("Could not send message to {}. Skipping...".format(user))
            del[msg_dict[list(msg_dict.keys())[0]]]
            time.sleep(random.randint(5, 10))
            counter += 1
            continue 

'''
for i in range(len(users)):
    del[msg_dict[list(msg_dict.keys())[0]]]
'''

with open('title_dict.json', 'w') as f:
    json.dump(msg_dict, f)



# -------------------------------------- FORMATTING --------------------------------------- #
print(f"\nSent DMs to {counter} users.")
print("\nInstagram Daily Follow Maximum: 200")
print("\nInstagram Hourly Follow Maximum: 10")
one_hour_from_now = datetime.datetime.now() + datetime.timedelta(hours=1)
print(f"\nYou can follow {10-counter} more users until {one_hour_from_now}.")
time.sleep(2)
print("\nAdding most recent execution to followers list...")
followers_list = open("followers.txt", 'a')
followers_delineated = '\n'.join(users)
followers_list.write(followers_delineated)
followers_list.write("\n")
time.sleep(2)
print(f"{len(msg_dict)} users remaining in database.\n")
print("\nSuccessfully added all followers. You can now close this window.")

