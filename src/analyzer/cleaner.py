import pandas as pd
import polyline


class Cleaner:
    activities = None

    def __init__(self, activities: pd.DataFrame):
        self.activities = activities

    def convert_data_types(self):
        # convert data types
        self.activities.loc[:, "start_date"] = pd.to_datetime(
            self.activities["start_date"]
        ).dt.tz_localize(None)
        self.activities.loc[:, "start_date_local"] = pd.to_datetime(
            self.activities["start_date_local"]
        ).dt.tz_localize(None)

    def convert_values(self):
        # convert values
        self.activities.loc[:, "distance"] /= 1000  # convert from m to km
        self.activities.loc[:, "average_speed"] *= 3.6  # convert from m/s to km/h
        self.activities.loc[:, "max_speed"] *= 3.6  # convert from m/s to km/h

    def set_index(self):
        # set index
        self.activities.set_index("start_date_local", inplace=True)

    def drop_columns(self):
        # drop columns
        self.activities.drop(
            [
                "map.summary_polyline",
                "resource_state",
                "external_id",
                "upload_id",
                "location_city",
                "location_state",
                "has_kudoed",
                "start_date",
                "athlete.resource_state",
                "utc_offset",
                "map.resource_state",
                "athlete.id",
                "visibility",
                "heartrate_opt_out",
                "upload_id_str",
                "from_accepted_tag",
                "map.id",
                "manual",
                "private",
                "flagged",
            ],
            axis=1,
            inplace=True,
        )

    def decode_polylines(self):
        # add decoded summary polylines
        self.activities["map.polyline"] = self.activities["map.summary_polyline"].apply(
            polyline.decode
        )

    def __call__(self):
        self.decode_polylines()
        self.convert_data_types()
        self.convert_values()
        self.set_index()
        self.drop_columns()

        return self.activities
