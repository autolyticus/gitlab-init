#!/usr/bin/python3
'''

Creates a repo with the name being the first Command line argument
Both on Gitlab and Github
Uses gitlab as the origin

'''

# Import all the things
import sh
import os
from os.path import expanduser
from sh.contrib import git
import requests as r
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep

# A very simple cd context manager
from cd import cd

# Step 0: Input from the user

print()
userName = input("Enter username: ")
repoName = input("Enter repo name: ")

# Check if gitlab token is present
with open(expanduser('~/.local/.gitlabtoken'), 'rb') as f:
    gitlabAuth = f.read().decode().split('\n')[0]

# Check if github token is present
with open(expanduser('~/.local/.githubtoken'), 'rb') as f:
    githubAuth = f.read().decode().split('\n')[0]

# Step 1: Create the repos on remotes

# Try to create a new Gitlab repo with repo name
try:
    headers = {'Private-Token': gitlabAuth}
    response = r.post(
        'https://gitlab.com/api/v4/projects',
        json={
            "name": repoName,
            "visibility": "public"
        },
        headers=headers)
    response.raise_for_status()
except Exception as e:
    print()
    print(
        'Something went wrong with creating the GitLab repo, Already exists?')
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print(message)
    choice = input('Continue???(y/n)')
    if choice != 'y':
        os.exit(1)

# Try to create a new Github repo with repo name
try:
    headers = {'Authorization': 'token ' + githubAuth}
    response = r.post(
        'https://api.github.com/user/repos',
        json={
            "name": repoName,
            'private': False,
        },
        headers=headers)
    response.raise_for_status()
except Exception as e:
    print()
    print(
        'Something went wrong with creating the GitHub repo, Already exists?')
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print(message)
    choice = input('Continue???(y/n)')
    if choice != 'y':
        os.exit(1)

# Step 2: Add Github.com as a push mirror on Gitlab

# Set the command line options for chromium web driver
chrome_options = webdriver.ChromeOptions()

# Change this to your chrome data dir usually ~/.config/chromium/ on *nix
path = '~/.config/Chromium'
chrome_options.add_argument(f'user-data-dir={expanduser(path)}')
chrome_options.add_argument(f'class=selenium-chrome')

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get(
    f'''https://gitlab.com/{userName}/{repoName.replace('.', '-')}/settings/repository'''
)

# Wait for the page to load
# sleep(2)
# __import__('pdb').set_trace()

pushExpandButton = driver.find_element_by_xpath(
    '//*[@id="js-push-remote-settings"]/div[1]/button')
pushExpandButton.click()
# Wait for the animation to play out
sleep(0.1)

# checkBox = driver.find_element_by_id(
#     'project_remote_mirrors_attributes_0_enabled')
# if not checkBox.is_selected():
#     checkBox.click()

pushUrl = driver.find_element_by_id('url')
pushUrl.clear()
pushUrl.send_keys(f'https://{userName}@github.com/{userName}/{repoName}')
sleep(0.1)

select = Select(driver.find_element_by_id('mirror_direction'))
select.select_by_visible_text('Push')
sleep(1)

password = driver.find_element_by_id(
    'project_remote_mirrors_attributes_0_password')
password.clear()
password.send_keys(githubAuth)
sleep(0.1)

checkBox = driver.find_element_by_id('only_protected_branches')
if checkBox.is_selected():
    checkBox.click()
sleep(0.1)

pushUrl.submit()
sleep(2)
# __import__('pdb').set_trace()
driver.close()

# Step 3: Init the new git repo and add gitlab as origin

sh.mkdir('-p', repoName)
with cd(repoName):
    try:
        git.init()
    except Exception as e:
        print(
            'Something went wrong with executing git init. Maybe the repo is already initialised?\n'
        )
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
        choice = input('Continue???(y/n)')
        if choice != 'y':
            os.exit(1)

    git.remote.add.origin(f'https://gitlab.com/{userName}/{repoName}')

print()
print(
    f"All done! An empty repo {repoName} has been initialised at ./{repoName} with remote pre-configured."
)
print("Happy pushing!")
