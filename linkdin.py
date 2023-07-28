import requests
import time
import re
import csv
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os as system

timeout = 10
email = 'email'
password = 'pass'

def scrape(driver, link):
    login(driver)
    time.sleep(1)
    link = f'{link}/posts/'
    driver.get(link)

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
 
    posts = soup.find_all('div', {'class': 'occludable-update'})
    
    postsString = [str(post) for post in posts]

    print(f'quantidade de posts {len(posts)}')
    results = []
    for post in postsString:
        results.append(getPostInformation(post))

    return results

        

def getPostInformation(post):
    postDescription = getPostDescription(post)
    hashtags = getHashtags(postDescription)
    likes = getLikes(post)
    comments = getComments(post)
    reposts = getReposts(post)
    type = getType(post)
    postLink = getLink(post)
    return [postDescription, hashtags, likes, comments, reposts, type, postLink]

def getPostDescription(post):
    try:
        postDescription = post.split('<span class="break-words">')[1]
        postDescription = postDescription.split('</span>')[0]
        postDescription = postDescription.split('<span dir="ltr">')[1]
        postDescription = postDescription.replace('<br/><br/>', '\n\n')
        # Remover tags HTML usando regex
        postDescription = re.sub(r'<.*?>', '', postDescription)
    except:
        postDescription = ""
    
    return postDescription


def getHashtags(description):
    rawData = description.split("#")
    hashtags = []
    for index, hashtag in enumerate(rawData):
        if(index != 0):
            hashtag = hashtag.split(" ")[0]
            hashtag = hashtag.split("\n")[0]
            hashtags.append(f'#{hashtag}')
    return hashtags

def getLikes(post):
    try:
        likes = post.split('social-details-social-counts__reactions-count">')[1]
        likes = likes.split('</span>')[0].strip()
    except:
        likes = 0
    return likes

def getComments(post):
    try:
        comments = post.split(' comments')[1]
        comments = comments.split('<span aria-hidden="true">')[1].strip()
    except:
        comments = 0
    return comments

def getReposts(post):
    try:
        reposts = post.split(' reposts')[1]
        reposts = reposts.split('aria-hidden="true">')[1].strip()
    except:
        reposts = 0
    return reposts

def getType(post):
    if(post.__contains__('update-components-image')):
        type = 'Image'
    else:
        type = 'Video'
    return type

def getLink(post):
    try:
        postlink = post.split('data-urn="')[1].split('"')[0]
        postlink = f'https://www.linkedin.com/feed/update/{postlink}'
    except:
        postlink = ""
    return postlink

def __prompt_email_password():
    u = input("Email: ")
    # p = getpass.getpass(prompt="Password: ")
    p =''
    return (u, p)

def page_has_loaded(driver):
        page_state = driver.execute_script('return document.readyState;')
        return page_state == 'complete'

def login(driver):

    # if not email or not password:
    #     email, password = __prompt_email_password()

    driver.get("https://www.linkedin.com/login")
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element(By.ID,"username")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.ID,"password")
    password_elem.send_keys(password)
    password_elem.submit()

    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        remember = driver.find_element(By.ID, "remember-me-prompt__form-primary")
        if remember:
            remember.submit()

    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "global-nav__primary-link")))

def main():
    print("Creating driver...")
    driver = webdriver.Chrome()
    link = "https://www.linkedin.com/company/quantropi/"
    results = scrape(driver, link)
    print(results)

if __name__ == '__main__':
    main()
