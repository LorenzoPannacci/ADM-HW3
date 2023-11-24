# import config
from functions.config import *
from functions import engine

# import libraries
import os
import pandas as pd
from tqdm.notebook import tqdm
import folium
from geopy.geocoders import Bing
import branca
import numpy as np

def load_all_courses():
    # load courses dataset
    courses_columns = ["courseName", "universityName", "facultyName", "isItFullTime", "description", "startDate", "fees", "modality", "duration", "city", "country", "administration", "url"]
    courses_df = pd.DataFrame(columns = courses_columns)

    for i in tqdm(range(n_courses)):
        file_path = tsvs_path + "course_" + str(1 + i) + ".tsv"
        df = pd.read_csv(file_path, sep = '\t')
        courses_df = pd.concat((courses_df, df), ignore_index = True)

    # remove those courses whose page was not avaiable
    courses_df = courses_df.dropna(subset = ["courseName"])
    return courses_df

def get_coordinates_table(api_key):
    '''
    Create (if necessary) and load the coordinates table
    '''

    # if already created don't waste api calls
    if os.path.exists(coordinates_table_path):
        print("Table already created!")
        coordinates_df =  pd.read_csv(coordinates_table_path)

    else:
        print("Creating table...")

        courses_df = load_all_courses()

        coordinates_df = pd.DataFrame(columns = ["universityName", "city", "country", "latitude", "longitude"])
        grouped = courses_df.groupby(["universityName", "city", "country"])

        # we check the coordinates of every university
        for group_name, group in tqdm(grouped, total = len(grouped)):
            location_string = group_name[0] + ", " + group_name[1] + ", " + group_name[2] # compose the address
            geolocator = Bing(api_key = api_key) # give the geolocator the api key
            location = geolocator.geocode(location_string, timeout = None) # execute the geolocation

            # create new row and insert entry ti dataframe
            new_row = pd.DataFrame({"universityName": [group_name[0]],
                                    "city": [group_name[1]],
                                    "country": [group_name[2]],
                                    "latitude": [location.latitude],
                                    "longitude": [location.longitude]})
            coordinates_df = pd.concat((coordinates_df, new_row), ignore_index = True)

        coordinates_df.to_csv("data/coordinates_table.csv", index = False)

    return coordinates_df

def visualize_map(query, coordinates_df):
    courses_df = load_all_courses()

    # for markers colors

    min_fee = courses_df["fees (EUR)"].min()
    max_fee = courses_df["fees (EUR)"].max()

    if np.isnan(min_fee):
        min_fee = 0
    if np.isnan(max_fee):
        max_fee = 0

    # create legend

    colormap = branca.colormap.linear.YlOrRd_07.scale(min_fee, max_fee)
    colormap = colormap.to_step(index=np.linspace(min_fee, max_fee, num = 50))
    colormap.caption = 'Fees cost (unknown is light blue)'

    # create empty world map centered on Rome
    map = folium.Map(location = [41.902782, 12.496366], max_bounds = True, min_zoom = 2)

    # we add a single marker per city
    for group_tuple, group in courses_df.groupby(["universityName", "city", "country"]):
        # get coordinates of marker
        coordinates_row = coordinates_df[(coordinates_df["universityName"] == group_tuple[0]) & (coordinates_df["city"] == group_tuple[1]) & (coordinates_df["country"] == group_tuple[2])]

        # get address
        description_string = "<b>" + group_tuple[0] + ", " + group_tuple[1] + ", " + group_tuple[2] + "</b>" + "<br>"

        # get courses infos
        for i, course in group.iterrows():
            description_string += "<br>" + "<b>" + "Course name: " + "</b>" + course["courseName"] + "<br>" + "<b>" + "Fees: " + "</b>"

            if pd.isna(course["fees (EUR)"]):
                description_string += "not found" + "<br>"
            else:
                description_string += str(course["fees (EUR)"]) + " EUR" + "<br>"

        # create marker
        iframe = folium.IFrame(description_string)

        popup = folium.Popup(iframe,
                            min_width=500,
                            max_width=500)
        
        # get marker color:
        reference_fee = group["fees (EUR)"].min()

        if pd.isna(reference_fee):
            color = "lightblue"
        else:
            color = colormap.rgba_hex_str(float(reference_fee))

        folium.Marker(
                    location = [coordinates_row["latitude"].item(), coordinates_row["longitude"].item()],
                    popup = popup,
                    icon = folium.Icon(icon = "solid fa-school-flag", prefix = "fa", icon_color = color, color = "gray"),
                    ).add_to(map)

    # add legend
    colormap.add_to(map)

    # display map
    return map