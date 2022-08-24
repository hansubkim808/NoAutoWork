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

# -------------------------------------------------- OPEN SELENIUM -------------------------------------------------------
PATH = "C:\\Program Files (x86)\\chromedriver.exe"

options = Options()
options.add_argument("user-data-dir=C:\\Users\\hansu\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
options.add_argument("profile-directory=Profile 2")

artist_keywords = ['music.empi.re', 'youtube.com', 'linktr.ee', 'soundcloud', 'mymixtapez', 'audiomack', 'spinrilla', 
                   'music.apple.com', 'apple music', 'spotify', 'tidal', 'spnr.la', 'unitedmasters.com', 'li.sten.to', 
                   'manylink.co', 'smarturl.it', 'youtube', 'bookings', 'features', 'features/bookings', 'rapper', 
                   'artist', 'musician', 'musician/band', 'out now', 'youtu.be', 'distrokid.com', ]

username_keywords = ['music']

def instagramParse(user):
    driver = Chrome(executable_path=PATH, options=options)
    driver.get(f'https://www.instagram.com/{user}')
    time.sleep(random.randint(5, 8))
    user_following_href = f'/{user}/followers/'

    # OLD 
    #df = pd.DataFrame(columns=['Artist IG', 'Followers', 'Following', 'F/F Ratio', 'Bio', 'Source'])
    #title = f'{user} Artist Network Analysis'
    #df.style.set_caption(title) 

    # NEW 
    df = pd.read_csv('testing.csv') if path.exists('testing.csv') else pd.DataFrame(columns=['Artist IG', 'Followers', 'Following', 'F/F Ratio', 'Bio', 'Source'])
    

    people_they_follow = driver.find_element_by_xpath("//a[@href='{}']".format(user_following_href))
    people_they_follow.click() 

    #num_following = int(people_they_follow.text[:3])
    num_following = 25000
    time.sleep(random.randint(2, 4))

    fBody = driver.find_element_by_xpath("//div[@class='isgrP']")
    scrolling_times=(num_following//4)
    scroll = 0
    counter = 0
    scroll_count = scrolling_times+5 
    timeout = time.time() + 60*60
    try:
        while scroll < scroll_count:
            try:
                if time.time() > timeout:
                    break

                if counter % 2 == 0:
                    followers_list = driver.find_elements_by_xpath("//a[@class='FPmhX notranslate  _0imsa ']")[(6*counter):]
                    pyautogui.moveTo(560, 375)
                    for follower_name in followers_list[:-1]:
                        # Grab username 
                        ig_username = follower_name.text

                        # NEW
                        if ig_username in df['Artist IG'].tolist():
                            print("user is already in database. Moving on...")
                            time.sleep(2)
                            continue

                        # Hover over username
                        action = ActionChains(driver)
                        action.move_to_element(follower_name).perform()
                        time.sleep(4)

                        # Grab quick bio
                        quick_bio =  driver.find_elements_by_xpath("//div[@class='_4BSuu']")
                        pop_up_bio = ' '.join(section.text for section in quick_bio) if len(quick_bio) > 0 else 'N/A'
                        print("Bio: " + pop_up_bio)

                        try: 
                            # Grab num followers + num following 
                            metrics = driver.find_elements_by_xpath("//span[@class=' _81NM2']")
                            followers = (metrics[1].text).split('\n')[0]
                            print(followers + " followers")
                            following = (metrics[2].text).split('\n')[0] 
                            print(following + " following")
                        except: 
                            # If not displayed then skip 
                            followers = "0"
                            following = "0"

                        # Skip if over a million followers, or over 100k 
                        if followers[-1] == 'm' or (followers[-1] == 'k' and float(followers[:-1]) > 100.0):
                            print("Too many followers. Skipping...")
                            time.sleep(3)
                            if pyautogui.position() == (1400, 450):
                                pyautogui.moveTo(560, 375)
                            elif pyautogui.position() == (560, 375):
                                pyautogui.moveTo(1400, 450)
                            time.sleep(1.5)
                            continue

                        # Convert followers/following into ints, calculate some metrics 
                        if followers[-1] == 'k':
                            if len(followers[:-1]) == 2:
                                int_followers = float(int(followers[:2])*1000)
                            elif len(followers[:-1]) == 4:
                                int_followers = float(float(followers[:4])*1000)
                        elif len(followers) == 5 and followers[1] == ',':
                            int_followers = int(followers[0] + followers[2:])
                        else:
                            int_followers = int(followers)

                        if following[-1] == 'k':
                            if len(following[:-1]) == 2:
                                int_following = float(int(following[:2])*1000)
                            elif len(following[:-1]) == 4:
                                int_following = float(float(following[:4])*1000)
                        elif len(following) == 5 and following[1] == ',':
                            int_following = int(following[0] + following[2:])
                        else:
                            int_following = int(following)

                        ff_ratio = float(int_followers/int_following) if int_following != 0 else 0

                        # If bio contains any relevant keywords/links, add to DF
                        if any(keyword in pop_up_bio for keyword in artist_keywords):
                            df = df.append(pd.DataFrame([[ig_username, followers, following, ff_ratio, pop_up_bio, user]], 
                                                columns=['Artist IG', 'Followers', 'Following', 'F/F Ratio', 'Bio', 'Source']), ignore_index=True)
                            print("Entry succesfully added.")
                        else:
                            print("No links found in bio. Moving on...")
                            pass

                        # Move cursor out of way 
                        if pyautogui.position() == (1400, 450):
                            pyautogui.moveTo(560, 375)
                        elif pyautogui.position() == (560, 375):
                            pyautogui.moveTo(1400, 450)
                        time.sleep(2)
                
                # Scroll down a full page length 
                driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                    fBody)
                time.sleep(random.randint(3, 6))
                scroll += 1
                counter += 1
            except:
                print("Keyboard interrupt. Exiting...")
                break
    except:
        pass 

    print("Parsing complete. Building database...")
    time.sleep(random.randint(2, 5))

    artist_csv = df.to_csv('testing.csv', index=False)
    print("Database successfully updated at testing.csv.")
    driver.close()

#------------------------ PARSING LINK, GATHERING TITLE INFORMATION ------------------------------- 

def songParse(csv, user):
    driver = Chrome(executable_path=PATH, options=options)
    title_dict = {}
    df = pd.read_csv(csv)
    accounts_to_parse = df.loc[df['Source'] == user]

    for i in range(accounts_to_parse.shape[0]):
        try:
            # NEW
            ig_username = accounts_to_parse['Artist IG'].tolist()[i]
            bio_text = accounts_to_parse['Bio'].tolist()[i]
            bio_list = bio_text.split(' ')

            # OLD
            #ig_username = df.loc[i, 'Artist IG']
            #bio_list = df.loc[i, 'Bio'].split(' ')
            # extract the link string from bio 
            if 'floodonthetrack' in bio_list: 
                continue
            link = ([s for s in bio_list if any(keyword in s for keyword in artist_keywords)])[0]
            print(link)
            timeout = time.time() + 60
            if time.time() > timeout:
                song_title = 'N/A'
                title_dict[ig_username] = song_title
                continue
            time.sleep(3)
            driver.get(link)
            time.sleep(10)

            # control flow for SoundCloud 
            if 'soundcloud' in link:
                try: 
                    # the link is a direct link to a song or album 
                    song_title = driver.find_element_by_xpath("//span[@class='soundTitle__title sc-font g-type-shrinkwrap-inline g-type-shrinkwrap-large-primary']").text
                except:
                    # the link is to a profile 
                    try:
                        profile_btn = driver.find_element_by_xpath("//div[@class='userBadge__title']")
                        profile_btn.click()
                        time.sleep(3) 
                        tracks = driver.find_elements_by_xpath("//li[@class='g-tabs-item']")[2]
                        tracks.click() 
                        time.sleep(3) 
                        song_title = driver.find_elements_by_xpath("//a[@class='soundTitle__title sc-link-dark']")[0].text if driver.find_elements_by_xpath("//a[@class='soundTitle__title sc-link-dark']") else 'N/A'
                    except:
                        print("Could not find the title for this song. Moving on...")
                        song_title = 'N/A'
                        time.sleep(3) 
        
            elif 'youtube' in link or 'youtu.be' in link: 
                # the link is a direct link to a song or album 
                if 'channel' in (driver.current_url).split('/'):
                    song_title = driver.find_elements_by_xpath("//a[@id='video-title']")[0].text if driver.find_elements_by_xpath("//a[@id='video-title']") else 'N/A'
                else:
                    try: 
                        song_title = driver.find_element_by_xpath("//h1[@class='title style-scope ytd-video-primary-info-renderer']").text
                    except:
                        # the link is to a channel 
                        try: 
                            video_title_xpath = '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-shelf-renderer/div[1]/div[2]/yt-horizontal-list-renderer/div[2]/div/ytd-grid-video-renderer[1]/div[1]/div[1]/div[1]/h3/a'
                            song_title = driver.find_element_by_xpath(video_title_xpath)
                            print("YouTube Video from Channel Home Page: " + song_title)
                        except:
                            print("Could not find the title for this song. Moving on...")
                            song_title = 'N/A'
                            time.sleep(3)
        
            elif 'audiomack' in link:
                try: 
                    song_title = driver.find_elements_by_xpath("//span[@class='music__heading--title']")[0].text
                except:
                    print("Could not find the title for this song. Moving on...")
                    song_title='N/A'
                    time.sleep(3)

            elif 'spinrilla' in link or 'spnr.la' in link: 
                # the link is a direct link to a song 
                try: 
                    song_title = driver.find_element_by_xpath("//div[@class='Track__Metadata_Title text-truncate Track__Metadata_Title-md']").text
                except:
                    # the link is a direct link to an album
                    try:
                        song_title = driver.find_element_by_xpath("//div[@class='album-title mb-2']").text
                    except:
                        # the link is to a profile
                        try:
                            song_title = driver.find_elements_by_xpath("//div[@class='v-list-item__title']")[0].text if driver.find_elements_by_xpath("//div[@class='v-list-item__title']") else 'N/A'
                        except:
                            print("Could not find the title for this song. Moving on...")
                            song_title = 'N/A'
                            time.sleep(3) 
            
            elif 'tidal' in link:
                # the link is a direct link to a song 
                try: 
                    song_title = driver.find_element_by_xpath("//span[@class='elemental__text css-wj3znv elemental__text']").text
                except:
                    # link is to an album                                     
                    try:
                        song_title = driver.find_elements_by_xpath("//span[@class='titleText--13bjG table--inactive-title']")[0].text
                    except:
                        print("Could not find the title for this song. Moving on...")
                        song_title = 'N/A'
                        time.sleep(3) 
            
            elif 'apple' in link:
                # link is to a single or album
                try: 
                    song_title = driver.find_element_by_xpath("//h1[@class='product-name typography-large-title-semibold clamp-4']").text 
                except:
                    # link is to a profile 
                    try:    
                        song_title = driver.find_element_by_xpath("//li[@class='featured-name']").text
                    except:
                        # try grabbing a single from an album 
                        try:
                            song_title = driver.find_elements_by_xpath("//span[@class='list-lockup-track-content']")[0].text 
                        except:
                            print("Could not find the title for this song. Moving on...")
                            song_title = 'N/A'
                            time.sleep(3) 
            else:
                song_title = 'N/A'

            title_dict[ig_username] = song_title
        except:
            continue
    driver.close()
    with open('title_dict.json', 'w') as f:
        json.dump(title_dict, f)
    return title_dict






