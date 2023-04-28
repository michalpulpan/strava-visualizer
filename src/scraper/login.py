# import modules
import requests
from os import environ as env

import urllib3

# disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


oauth_url = "https://www.strava.com/oauth/token"


# define function to get a new access token
def get_access_token():
    payload = {
        "client_id": env["client_id"],
        "client_secret": env["client_secret"],
        "refresh_token": env["refresh_token"],
        "grant_type": "refresh_token",
    }

    print("Requesting Token...\n")
    r = requests.post(oauth_url, data=payload, verify=False)
    print(r.text)
    access_token = r.json()["access_token"]
    print(r.json())
    print("Access Token = {}\n".format(access_token))
    return access_token
