#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re


URL = 'https://moodle.ntust.edu.tw/'
session = requests.session()


ua = UserAgent()
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en',  # 'zh-TW'
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '89',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '',
    'Host': 'moodle.ntust.edu.tw',
    'Origin': 'https://moodle.ntust.edu.tw',
    'Referer': 'https://moodle.ntust.edu.tw/login/index.php',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': ua.random,
}


def getCookies(cookie_jar, domain):
    cookie_dict = cookie_jar.get_dict(domain=domain)
    found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
    return ';'.join(found)


def login(id, pwd):
    global session, headers
    LOGIN = 'https://moodle.ntust.edu.tw/login/'
    data = {
        'username': id,
        'password': pwd,
        'rememberusername': 0,
        'anchor': '',
        'logintoken': ''
    }
    session = requests.session()
    res = session.get(URL, allow_redirects=False)  # get cookies
    soup = BeautifulSoup(res.text, 'html.parser')

    data['logintoken'] = soup.find('form', {'id': 'login'}).find('input', {'name': 'logintoken'})[
        'value']  # get logintoken
    headers['Cookie'] = getCookies(res.cookies, "moodle.ntust.edu.tw")

    res = session.post(LOGIN, headers=headers, data=data)  # login
    soup = BeautifulSoup(res.text, 'html.parser')

    # TODO: fix bug about <em><span></span>text</em>
    user = soup.find('div', {'class': ['usermenu', 'pull-right']}).find('em')

    if (user is not None):
        print("login success")
        # print(user)
        return True
    else:
        print("login fail")
        return False


def getcourse(id):
    global session
    PROFILE = 'https://moodle.ntust.edu.tw/user/profile.php?id=' + str(id) + '&showallcourses=1'
    res = session.get(PROFILE)
    soup = BeautifulSoup(res.text, 'html.parser')

    result = []
    s = soup.find('div', {'class': 'profile_tree'})
    if (s is not None):
        for course in s.find_all('a'):
            href = course.get('href')
            if (href.find('https://moodle.ntust.edu.tw/user/view.php?id=') != -1):
                c = re.split(r'[【】 ]', course.string, maxsplit=4)
                c.append(re.split(r'[=&]', course.get('href'))[3])
                result.append(c)
    return result


def personsearch(name, mycourses=False):
    global session, headers
    MESSAGE = 'https://moodle.ntust.edu.tw/message/index.php?usergroup=search&advanced=1'
    res = session.get(MESSAGE)
    soup = BeautifulSoup(res.text, 'html.parser')

    sesskey = soup.find('input', {'type': 'hidden', 'name': 'sesskey'})['value']  # get sesskey
    data = {
        'name': name,
        'personsubmit': 'Search for a person',
        'sesskey': sesskey,
        'keywords': '',
        'keywordsoption': 'allmine'
    }
    if (mycourses):
        data['mycourses'] = 'on'

    res = session.post(MESSAGE, data=data)
    soup = BeautifulSoup(res.text, 'html.parser')

    result = []
    for person in soup.find_all('td', {'class': 'contact'}):
        # p = [student_id, name, web_id]
        p = re.split(r'@ ', person.string)
        p.append(person.a.get('href').replace('https://moodle.ntust.edu.tw/message/index.php?id=', ''))
        result.append(p)
    return result


def personcourse(name):
    result = []
    person = personsearch(name)
    for p in person:
        c = getcourse(p[-1])
        c.insert(0, p)
        result.append(c)
    return result
