from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located, presence_of_element_located
import time 
import datetime
import random 
import pandas as pd
import pyautogui
import pytesseract
import json
from os import path 
import re

PATH = "C:\\Program Files (x86)\\chromedriver.exe"
options = Options()
#options.add_argument("user-data-dir=C:\\Users\\xxxxxxxxxxxxxxx")
options.add_argument("profile-directory=Profile 2")


def PostCrawl(user):
    driver = Chrome(executable_path=PATH, options=options)
    driver.get(f'https://www.instagram.com/{user}/')
    time.sleep(random.randint(5, 8))

    df = pd.read_csv('leads.csv') if path.exists('leads.csv') else pd.DataFrame(columns=['IG_name(s)', 'Post Caption', 'Source'])

    first_post = driver.find_elements_by_xpath("//div[@class='eLAPa']")[0]
    first_post.click() 
    time.sleep(5)
    now = time.time()
    timeout = now + 3600
    right_arrow = driver.find_element_by_xpath("//a[@class=' _65Bje  coreSpriteRightPaginationArrow']")
    while right_arrow:
        try:
            if time.time() > timeout:
                print("Parsing duration reached. Finishing up...")
                break

            post_caption = driver.find_element_by_xpath("//div[@class='C4VMK']").text
            print(post_caption)
            username_list = set([s for s in post_caption.replace('\n', ' ').split() if s[0] == '@'])
            df = df.append(pd.DataFrame([[username_list, post_caption, user]], 
                                        columns=['IG_name(s)', 'Post Caption', 'Source']), ignore_index=True)

            print("\n")
            print(username_list)
            right_arrow = driver.find_element_by_xpath("//a[@class=' _65Bje  coreSpriteRightPaginationArrow']")
            right_arrow.click() 
            time.sleep(5)
        except KeyboardInterrupt:
            print("Keyboard Interrupt Detected. Finishing up...")
            break
        except:
            print("Unexpected system error. Finishing...")
            break

    print("Parsing complete. Building database...")
    time.sleep(random.randint(2, 5))

    artist_csv = df.to_csv('leads.csv', index=False)
    print("Database successfully updated at leads.csv.")
    time.sleep(3)
    driver.close()

'''
    first_post_caption = driver.find_elements_by_xpath("//div[@class='C4VMK']")[0].text
    username_list = set([s for s in first_post_caption.split(" ") if s[0] == '@'])
    df = df.append(pd.DataFrame([[username_list, first_post_caption, user]], 
                                columns=['IG_name(s)', 'Post Caption', 'Source']), ignore_index=True)

    right_arrow = driver.find_element_by_xpath("//a[@class=' _65Bje  coreSpriteRightPaginationArrow']")
    right_arrow.click() 
    time.sleep(5)
'''