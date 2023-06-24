import requests
import config as cfg


def payload():  # get payload data from config file
    return ({"username": cfg.mashov["username"],
             "password": cfg.mashov["password"],
             "semel": cfg.mashov["semel"],
             "year": cfg.mashov["year"]})


login = requests.post('https://web.mashov.info/api/login', json=payload())


def get_header(method):  # returns required header with appropriate method
    token = login.headers.get('x-csrf-token')
    cookie = login.headers.get('Set-Cookie')

    return ({
    'method': str(method),
    'x-csrf-token': token,
    'cookie': cookie
    })


userid = login.text[127:163]
BASEURL = "https://web.mashov.info/api/students/" + userid + "/"