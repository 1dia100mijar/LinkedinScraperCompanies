# LinkedinScraperCompanies
Program to scrape all the post in a company profile


### Before running the program, make sure to have installed the following packages:
- bs4 
- selenium
- getpass

You can install all at once with the following command:
> pip install bs4 selenium getpass


### Log in credentials
Leave the line the following line of code uncomment, and provide the credentials everytime you run the program:
```
username, password = __prompt_email_password()
```
or in alternative insert yout Linkedin's account **username** and **password** on the lines:
```
username = "Enter your username here"
password = "Enter your password here"
```

## 🚨Browser compatibilities🚨
The program is designed use the Chrome browser. You can change it to one that is supported by the Selenium library, when the driver is being created in the line of code:
```
driver = webdriver.Chrome()
```
Keep in mind that using other browsers, the final result isn't garanteed to be the same.
