import folium
import numpy as np
import polyline


class Plotter:
    activities = None

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

    def __call__(self):
        pass
