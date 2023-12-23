# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import numpy as np
import altair as alt
import os
from pandas import json_normalize

api_key = os.environ.get("yelp_api_key")

#API request
url = "https://api.yelp.com/v3/businesses/search?location=los%20angeles&term=ramen&sort_by=review_count&limit=50"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer {api_key}"
}
response = requests.get(url, headers=headers)

# Creates Original dataframe from Response
data = response.json()
df_ramen = json_normalize(data["businesses"])

# Adds additional column with ramen prices
prices = [19.5,
    16.5,
    14.95,
    22.65,
    19,
    19,
    14.95,
    18.49,
    14,
    18.8,
    20.55,
    14.45,
    14.95,
    20.5,
    18.98,
    13.38,
    16.99,
    19.75,
    16.5,
    18.9,
    19,
    15.5,
    18,
    16,
    16.5,
    15.62,
    13.99,
    13,
    18.5,
    17.5,
    17.83,
    16,
    15.99,
    19,
    15,
    19,
    15.5,
    18,
    18.8,
    19.95,
    21.05,
    15.5,
    21,
    15.5,
    19.99,
    17.6,
    16.75,
    14.95,
    18,
    26,
]
df_ramen["prices"] = prices

# Creates new column popularity score
def calculate_popularity_score(avg_rating, num_reviews, weight=0.5):
    popularity_score = (weight * avg_rating) + ((1 - weight) * np.log(num_reviews + 1)) - 2
    return round(popularity_score, 2)
df_ramen['Popularity'] = df_ramen.apply(lambda row: calculate_popularity_score(row['rating'], row['review_count']), axis=1)

# Creates new columns for location as floats
df_ramen["latitude"] = df_ramen["coordinates.latitude"].astype(float)
df_ramen["longitude"] = df_ramen["coordinates.longitude"].astype(float)

# Creates new columns for address as string
df_ramen["Address"] = df_ramen["location.address1"].astype(str)

# Creates new dataframe to display
df_display=df_ramen[["name","Address","Popularity","prices"]].copy()

# Streamlit app
st.set_page_config(
    page_title="Ramen For Katie",
    page_icon="🍜",  # Set a favicon for the page
)

# Displays new dataframe
st.title("Ramen for Katie 🍜")
st.divider()
st.subheader("Top 50 Ramen Spots in LA")
st.dataframe(df_display, use_container_width=True, hide_index=True)
st.divider()

# Displays scatterplot
st.subheader("Popularity vs. Price")
chart = alt.Chart(df_ramen).mark_circle().encode(
    x=alt.X("Popularity", scale=alt.Scale(domain=(2.5, 5))),  # Set the x-axis scale
    y=alt.Y("prices", scale=alt.Scale(domain=(10,30))),  # Set the y-axis scale to log scale
    size="review_count",
    tooltip=["name", "rating", "review_count","Popularity","prices","Address"],
).interactive()
st.altair_chart(chart, use_container_width=True)
st.divider()

# Displays map of ramen spots

tooltip_text = {"html": "Name: <b>{name}</b><br>Rating: {rating}<br>Price: {price}"}
st.subheader("Ramen Map")
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=df_ramen['coordinates.latitude'].mean(),
        longitude=df_ramen['coordinates.longitude'].mean(),
        zoom=10,
        pitch=50,
        use_container_width=True,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df_ramen,
            get_position=['longitude', 'latitude'],
            get_radius = [200],
            get_fill_color=[255, 20, 20],
            tooltip=tooltip_text,
            pickable=True,
        ),
        pdk.Layer(
            "TextLayer",
            data=df_ramen,
            get_position="[longitude, latitude]",
            get_text="name",  # Display restaurant names
            get_color="[0, 0, 0, 255]",  # Black text color
            size_scale=.5,  # Font size
            pickable=True,
        )
    ],
))
