import time
import requests
from .login import get_access_token
from tqdm import tqdm
import json
import urllib3

# disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


activities_url = "https://www.strava.com/api/v3/athlete/activities"


def get_elevation(locations):
    base_url = "https://api.opentopodata.org/v1/eudem25m"
    payload = {"locations": f"{'|'.join(locations)}"}
    r = requests.get(base_url, params=payload)
    print(r.text)
    r = r.json()["results"]

    ret = {}

    for result in r:
        ret[f"{result['location']['lat']},{result['location']['lng']}"] = result[
            "elevation"
        ]
    # this should return a dictionary with the following structure:
    # {
    #     "lat1,lng1": elevation1,
    #     "lat2,lng2": elevation2,
    #     ...
    # }
    return ret


class Scraper:
    access_token = None

    def __init__(self):
        self.access_token = get_access_token()

    # define function to get your strava data
    def get_data(self, access_token, per_page=200, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {"per_page": per_page, "page": page}

        data = requests.get(activities_url, headers=headers, params=params).json()
        return data

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

    def grab_elevation_data(self, activities):
        # divide data into chunks of 100
        location_elevation = {}

        # filter only top activities with highest elevation
        top_elevations = activities.sort_values(
            by="total_elevation_gain", ascending=False
        )[:10]

        for activity in top_elevations["map.polyline"]:
            for cord in activity:
                location_elevation[f"{cord[0]},{cord[1]}"] = None
        print("locations_elevation", location_elevation)
        # get elevation data
        # convert location_elevation to list list of lists of 100
        location_elevation_list = []
        location_elevation_dict = {}
        for i in range(0, len(location_elevation), 100):
            location_elevation_list.append(list(location_elevation.keys())[i : i + 100])
        print(location_elevation_list)
        for i in tqdm(range(len(location_elevation_list))):
            location_elevation_dict = {
                *location_elevation_dict,
                *get_elevation(location_elevation_list[i]),
            }
            # wait 1s to avoid overloading the server
            time.sleep(1)
        print(location_elevation_dict)
        # convert location_elevation_list to dictionary

        with open("./data/location_elevation.json", "w") as outfile:
            json.dump(location_elevation_dict, outfile)
