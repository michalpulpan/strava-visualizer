import base64
import json
import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import polyline
from folium.plugins import HeatMap
from sklearn.cluster import KMeans
from tqdm import tqdm
import requests
import time

from geopy import distance


# def get_elevation(latitude, longitude):
#     base_url = "https://api.opentopodata.org/v1/eudem25m"
#     payload = {"locations": f"{latitude},{longitude}"}
#     r = requests.get(base_url, params=payload)
#     print(r.text)
#     r = r.json()["results"][0]

#     return r["elevation"]


class Plotter:
    activities = None
    m = None

    def __init__(self, activities):
        self.activities = activities

    def single_random_plot(self):
        # select one activity
        my_ride = self.activities.iloc[0, :]  # first activity (most recent)
        print(my_ride["map.polyline"][0])
        # plot ride on map
        centroid = [
            np.mean([coord[0] for coord in my_ride["map.polyline"]]),
            np.mean([coord[1] for coord in my_ride["map.polyline"]]),
        ]
        m = folium.Map(location=centroid, zoom_start=10)
        folium.PolyLine(my_ride["map.polyline"], color="red").add_to(m)
        folium.TileLayer("Stamen Terrain").add_to(m)
        m.save("mymap.html")

    def all_activities_plot(self):
        # calculate centroid of all rides
        centroid = [
            np.mean(
                [
                    np.mean([coord[0] for coord in ride])
                    for ride in self.activities["map.polyline"]
                ]
            ),
            np.mean(
                [
                    np.mean([coord[1] for coord in ride])
                    for ride in self.activities["map.polyline"]
                ]
            ),
        ]
        print(centroid)

        # plot all rides on map
        m = folium.Map(location=centroid, zoom_start=10)
        # for ride in self.activities["map.polyline"]:
        #     folium.PolyLine(ride, color="red", opacity=0.3).add_to(m)
        folium.TileLayer("Stamen Terrain").add_to(m)
        m.save("mymap.html")
        self.m = m
        return self.m

    def add_heatmap(self):
        # add heatmap to self.m
        points = self.activities.explode("map.polyline")["map.polyline"]
        HeatMap(
            points,
            radius=4,
            blur=4,
            min_opacity=0.5,
            gradient={0.4: "blue", 0.65: "lime", 1: "red"},
        ).add_to(self.m)
        self.m.save("myheatmap.html")
        return self.m

    def general_plot(self):
        """
        plot km per month
        """
        distance_by_month = pd.pivot_table(
            self.activities,
            values="distance",
            index="month",
            columns="type",
            aggfunc="sum",
        )

        # Plot the pivot table as a stacked bar chart
        distance_by_month.plot(kind="bar", stacked=True, figsize=(10, 6))
        plt.title("Activity Distance by Month")
        plt.xlabel("Month")
        plt.ylabel("Distance (km)")
        plt.savefig("distance_by_month.png")
        """
        plot km per year
        """
        distance_by_month = pd.pivot_table(
            self.activities,
            values="distance",
            index="year",
            columns="type",
            aggfunc="sum",
        )

        # Plot the pivot table as a stacked bar chart
        distance_by_month.plot(kind="bar", stacked=True, figsize=(10, 6))
        plt.title("Activity Distance by year")
        plt.xlabel("Year")
        plt.ylabel("Distance (km)")
        plt.savefig("distance_by_year.png")

    def general_plot_weeks(self):
        # Filter for activities in years 2021-2023
        # print(self.activities.head())

        activities = self.activities[
            pd.to_datetime(self.activities["start_date_local"]).dt.year.isin(
                [2021, 2022, 2023]
            )
        ]
        # Group activities by week and year and calculate the sum of distance, elevation gain, and average speed
        weekly_summary = activities.groupby(
            [
                pd.Grouper(key="start_date_local", freq="W-MON"),
                pd.to_datetime(activities["start_date_local"]).dt.year,
            ]
        ).agg(
            {"distance": "sum", "total_elevation_gain": "sum", "average_speed": "mean"}
        )
        # weekly_summary = weekly_summary.reset_index(drop=False)
        weekly_summary["start_date_local_year"] = weekly_summary.index.get_level_values(
            1
        )
        weekly_summary["week_start"] = weekly_summary.index.get_level_values(0)

        # create week number column
        weekly_summary["week_number"] = (
            weekly_summary["week_start"].dt.isocalendar().week
        )

        # Plot the distance, elevation gain, and average speed by week for each year
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(12, 12), sharex=True)

        for year in [2021, 2022, 2023]:
            year_data = weekly_summary[weekly_summary["start_date_local_year"] == year][
                :-1
            ]
            print(year_data.head())
            ax1.plot(year_data["week_number"], year_data["distance"], linewidth=2)
            ax2.plot(
                year_data["week_number"],
                year_data["total_elevation_gain"],
                linewidth=2,
            )
            ax3.plot(year_data["week_number"], year_data["average_speed"], linewidth=2)

        ax1.set_ylabel("Distance (km)")
        ax1.set_xlabel("Week")
        ax1.legend(["2021", "2022", "2023"], loc="upper left")

        ax2.set_xlabel("Week")
        ax2.set_ylabel("Elevation Gain (m)")
        ax2.legend(["2021", "2022", "2023"], loc="upper left")

        ax3.set_ylabel("Average Speed (km/h)")
        ax3.set_xlabel("Week")
        ax3.legend(["2021", "2022", "2023"], loc="upper left")

        plt.suptitle(
            "Activity Distance, Elevation Gain, and Average Speed by Week for 2021-2023"
        )
        plt.savefig("weekly_summary.png")
        # plt.show()

    def grab_elevation_data(self, activities):
        def get_elevation(locations):
            base_url = "https://api.opentopodata.org/v1/eudem25m"
            payload = {"locations": f"{'|'.join(locations)}"}
            r = requests.get(base_url, params=payload)
            print(r.text)
            r = r.json()["results"]

            ret = {}

            for result in r:
                ret[
                    f"{result['location']['lat']},{result['location']['lng']}"
                ] = result["elevation"]
            # this should return a dictionary with the following structure:
            # {
            #     "lat1,lng1": elevation1,
            #     "lat2,lng2": elevation2,
            #     ...
            # }
            return ret

        # divide data into chunks of 100
        location_elevation = {}

        # try to load "./data/location_elevation.json"
        try:
            with open("./data/location_elevation.json", "r") as f:
                location_elevation = json.load(f)
                return location_elevation
        except:
            pass

        for activity in activities["map.polyline"]:
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
                **location_elevation_dict,
                **get_elevation(location_elevation_list[i]),
            }
            # wait 1s to avoid overloading the server
            time.sleep(1)
        print(location_elevation_dict)
        # convert location_elevation_list to dictionary

        with open("./data/location_elevation.json", "w") as outfile:
            json.dump(dict(location_elevation_dict), outfile)

    def plot_top_elevations(self):
        # get activites with most elevation gain
        top_elevations = self.activities.sort_values(
            by="total_elevation_gain", ascending=False
        )[:10]

        location_elevation = self.grab_elevation_data(top_elevations)
        print(location_elevation)
        # iterate through top_elevations and get elevation data for each activity and plot
        for index, activity in top_elevations.iterrows():
            elevation_data = []
            distances = []
            # print(activity["map.polyline"])
            prev_cord = None
            for cord in activity["map.polyline"]:
                cord_code = f"{cord[0]},{cord[1]}"
                if cord_code in location_elevation:
                    # print(location_elevation[cord_code])
                    elevation_data.append(location_elevation[cord_code])
                else:
                    print("no elevation data")

                # create list of distances for each elevation data point (in km) for plotting purposes
                if len(distances) == 0:
                    distances.append(0)
                else:
                    distances.append(
                        distances[-1]
                        + distance.geodesic(
                            (prev_cord[0], prev_cord[1]), (cord[0], cord[1] + 0.001)
                        ).km
                    )
                prev_cord = cord

            print("Distances", distances)

            activity["map.elevation"] = elevation_data
            fig, ax = plt.subplots(figsize=(10, 4))
            # ax = (
            #     pd.Series(activity["map.elevation"])
            #     .rolling(3)
            #     .mean()
            #     .plot(ax=ax, color="steelblue", legend=False)
            # )
            ax.plot(distances, elevation_data, color="steelblue", linewidth=2)

            ax.set_ylabel("Elevation")
            ax.set_xlabel("Distance (km)")
            ax.axes.xaxis.set_visible(True)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.set_title(
                f"Elevation Profile for {activity['name']} ({activity['start_date_local']})"
            )
            plt.savefig(f"./plots/{index}.png")
            # plt.show()

    def make_map_of_top_elevations(self):
        # get activites with most elevation gain
        top_elevations = self.activities.sort_values(
            by="total_elevation_gain", ascending=False
        )[:10]

        location_elevation = self.grab_elevation_data(top_elevations)
        print(location_elevation)

        # get centroid of top_elevations and plot map
        centroid = [
            np.mean([coord[0] for coord in top_elevations["map.polyline"]]),
            np.mean([coord[1] for coord in top_elevations["map.polyline"]]),
        ]

        resolution, width, height = 75, 6, 6.5

        # plot map
        m = folium.Map(location=centroid, zoom_start=10)
        elevation_profile = {}
        # iterate through top_elevations and get elevation data for each activity and plot
        for index, activity in top_elevations.iterrows():
            elevation_data = []
            distances = []
            # print(activity["map.polyline"])
            prev_cord = None
            for cord in activity["map.polyline"]:
                cord_code = f"{cord[0]},{cord[1]}"
                if cord_code in location_elevation:
                    # print(location_elevation[cord_code])
                    elevation_data.append(location_elevation[cord_code])
                else:
                    print("no elevation data")

                # create list of distances for each elevation data point (in km) for plotting purposes
                if len(distances) == 0:
                    distances.append(0)
                else:
                    distances.append(
                        distances[-1]
                        + distance.geodesic(
                            (prev_cord[0], prev_cord[1]), (cord[0], cord[1] + 0.001)
                        ).km
                    )
                prev_cord = cord

            activity["map.elevation"] = elevation_data
            activity["map.distances"] = distances

            folium.PolyLine(activity["map.polyline"], color="red").add_to(m)
            elevation_profile[index] = base64.b64encode(
                open(f"./plots/{index}.png", "rb").read()
            ).decode()

            # popup
            html = f"""
            <h3>{activity['name']}</h3>
            <p>{activity['start_date_local']}</p>
            <img src="data:image/png;base64,{elevation_profile[index]}"
            width="100%" height="auto"
            >
            """
            # add marker to map
            iframe = folium.IFrame(
                html=html,
                width=(width * resolution) + 20,
                height=(height * resolution) + 20,
            )
            popup = folium.Popup(iframe, max_width=2650)
            folium.Marker(
                location=activity["map.polyline"][0],
                popup=popup,
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(m)

        m.save("elevation_map.html")

    def __call__(self):
        pass
