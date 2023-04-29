import folium
import numpy as np
import polyline
from folium.plugins import HeatMap


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

    def __call__(self):
        pass
