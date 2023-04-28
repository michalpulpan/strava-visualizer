import requests
from .login import get_access_token
from tqdm import tqdm
import json
import urllib3

# disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


activities_url = "https://www.strava.com/api/v3/athlete/activities"


class Scraper:
    access_token = None

    def __init__(self):
        self.access_token = get_access_token()

    def __call__(self):
        # get the strava data
        max_number_of_pages = 10
        data = list()
        for page_number in tqdm(range(1, max_number_of_pages + 1)):
            page_data = self.get_data(self.access_token, page=page_number)
            if page_data == []:
                break
            data.append(page_data)
        # data dictionaries
        data_dictionaries = []
        for page in data:
            data_dictionaries.extend(page)
        # print number of activities
        print(f"Number of activities downloaded: {len(data_dictionaries)}")

        # filter out activities that are not Ride
        for i in tqdm(range(len(data_dictionaries))):
            print(data_dictionaries[i])
            if data_dictionaries[i]["type"] != "Ride":
                data_dictionaries[i] = None
        data_dictionaries = list(filter(None, data_dictionaries))
        print(f"Number of activities after filtering: {len(data_dictionaries)}")

        with open("./data/activities.json", "w") as outfile:
            json.dump(data_dictionaries, outfile)

    # define function to get your strava data
    def get_data(self, access_token, per_page=200, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {"per_page": per_page, "page": page}

        data = requests.get(activities_url, headers=headers, params=params).json()
        return data
