#!/usr/bin/python3
'''

Creates a repo with the name being the first Command line argument
Both on Gitlab and Github
Uses gitlab as the origin
TODO: Setup push mirroring automatically on Gitlab -> Github

'''

from sys import argv
import sh
import os
from sh.contrib import git
import requests

repoName = argv[1]

# https://gitlab.com/reisub0/nim-chat/settings/repository
if not os.path.exists(os.path.join(os.getcwd(), '.git')):
    git.init()

try:
    sh.lab('project', 'create', repoName)
except:
    print('Something went wrong with creating the GitLab repo, Already exists?')
try:
    os.system('hub create')
except:
    print('Something went wrong with creating the GitHub repo, Already exists?')
# sh.echo('hi')
# def githubPublish(name,):
