import time
import re
import csv
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import getpass

timeout = 10

def scrape(driver, link):
    link = f'{link}/posts/'
    driver.get(link)

    time.sleep(3)

    posts = {}

    old_position = 0
    new_position = None
    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        time.sleep(1)           #experimentar tirar eleste limte de tempo, para ver se a execução do programa é mais rápida, como o programa está a fazer processamento pode ser que não seja nbecessáio o tempo de sleep como era preciso no insta. No insta apenas estava a fazer scrool sem nenhum processamento pelo meio
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        soup = str(soup)

        results = soup.split('occludable-update')
        
        # results = {}
        for result in results:
            try:
                postlink = result.split('data-urn="')[1].split('"')[0]
                postlink = f'https://www.linkedin.com/feed/update/{postlink}'
            except:
                postlink = ''
            
            if('linkedin' in postlink):
                posts[postlink] = result
        
        new_position = scroll(driver, old_position)

    print(f'\n\nFound {len(posts)} posts.')
    postsFiltered = []
    for postlink, post in posts.items():
        postInfo = getPostInformation(str(post))
        postInfo.append(postlink)
        postsFiltered.append(postInfo)

    return postsFiltered

def scroll(driver, old_position):
    next_position = old_position + 700
    driver.execute_script(f"window.scrollTo(0, {next_position});")
    # Get new position
    return driver.execute_script(("return (window.pageYOffset !== undefined) ?"
                " window.pageYOffset : (document.documentElement ||"
                " document.body.parentNode || document.body);"))        

def getPostInformation(post):
    descriptionInfo = getPostDescription(post)
    hashtags = getHashtags(descriptionInfo[0])
    likes = getLikes(post)
    comments = getComments(post)
    reposts = getReposts(post)
    type = getType(post)
    return [descriptionInfo[0], hashtags, likes, comments, reposts, type, descriptionInfo[1]]

def getPostDescription(post, f = 0):
    try:
        postDescription = post.split('<span class="break-words">')[1]
        postDescription = postDescription.split('</span>')[0]
        postDescription = postDescription.split('<span dir="ltr">')[1]
        postDescription = postDescription.replace('<br/><br/>', '\n\n')
        
        #Get Tags(users and websites)
        tags = postDescription.split('"https://')
        tagsFiltered = []
        for tag in tags:
            tag = tag.split(' ')[0]
            tag = tag.split('">')[0]
            if('www.linkedin.com/feed/hashtag' in  tag):
                continue
            else:
                if('.' in tag or '/' in tag):
                    tagsFiltered.append(tag)

        # Remover tags HTML usando regex
        postDescription = re.sub(r'<.*?>', '', postDescription)
    except:
        postDescription = ""
        tagsFiltered = []
    
    return [postDescription, tagsFiltered]


def getHashtags(description):
    rawData = description.split("#")
    hashtags = []
    for index, hashtag in enumerate(rawData):
        if(index != 0):
            hashtag = hashtag.split(" ")[0]
            hashtag = hashtag.split("\n")[0]
            try:
                hashtag = hashtag.split('\xa0')[0]
            except:
                hashtag = hashtag
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
    
    if(comments == 0):
        try:
            comments = post.split(' comment')[1]
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

    if(reposts == 0):
        try:
            reposts = post.split(' repost')[1]
            reposts = reposts.split('aria-hidden="true">')[1].strip()
        except:
            reposts = 0
    return reposts

def getType(post):
    if(post.__contains__('update-components-image')):
        type = 'Image'
    elif(post.__contains__('feed-shared-document__container')):
        type = 'Document'
    elif(post.__contains__('update-components-poll')):
        type = 'Pool'
    elif(post.__contains__('update-components-article')):
        type = 'Article'
    else:
        type = 'Video'
    return type

def __prompt_email_password():
    u = input("Email: ")
    p = getpass.getpass(prompt="Password: ")
    return (u, p)

def login(driver, email, password):
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

    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "global-nav__primary-link")))
    except:
        print("\nLog In Failed.")
        exit()
    time.sleep(1)

def initializeCSV(fileName, results):
    with open(fileName, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["description", "hashtags", "likes", "comments", "reposts", "type", "links/tags", "link"])
        for result in results:
            escaped_result = [item.replace("\n", r"\n") if isinstance(item, str) else item for item in result]
            writer.writerow(escaped_result)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def main():
    print("Welcome to the Linkedin Scraper")
    print("Please enter the following information")
    username = "Enter your username here"
    password = "Enter your password here"
    # username, password = __prompt_email_password()
    link = input("Company Link: ")
    fileName = input("File name: ")
    fileName = f'{fileName}.csv'
    fileDir = f"./{fileName}"

    start = time.time()

    print("Creating driver...")
    driver = webdriver.Chrome()
    login(driver, username, password)
    results = scrape(driver, link)
    driver.close()
    initializeCSV(fileDir, results)
    end = time.time()
    elapsedTime = end - start
    print(f'\n\nDone! Time elapsed: {convert(elapsedTime)} minutes')
    print(f'The csv file {fileName} was saved in the Results directory')

if __name__ == '__main__':
    main()
