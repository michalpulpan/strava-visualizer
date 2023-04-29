import polyline
import pandas as pd


class Transformer:
    activities = None

    def __init__(self, activities):
        self.activities = activities

    def transform_lines_2_points(self):
        # create new dataframe with points from polylines
        points = pd.DataFrame(self.activities)
        points = points.explode("map.polyline")
        # points = points.rename(columns={"map.summary_polyline": "map.polyline"})
        points = points.reset_index(drop=True)
        # points = points.drop(columns=["map.summary_polyline"])
        # points = points.dropna()
        # points = points.reset_index(drop=True)
        # points = points[
        #     ["map.polyline", "name", "distance", "average_speed", "moving_time"]
        # ]

        print(points.head())
        print(points.info())

        return points
