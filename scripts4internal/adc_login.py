import requests

homepage_url = 'http://10.110.23.4/'
login_page_url = f'{homepage_url}login/do_login'
session = requests.session()

homepage_response = session.get(homepage_url)
headers = {'username': 'nsroot', 'password': '72hhj@8yr4B'}

if homepage_response.status_code == 200:
    print('Success reaching home homepage')
    loginpage_response = session.post(login_page_url, headers=headers)
    print(loginpage_response)