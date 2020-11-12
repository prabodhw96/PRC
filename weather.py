import numpy as np
import pandas as pd
import pycountry
import streamlit as st

st.title("Daily Weather Information")
st.markdown("Reported by NOAA")

weather = pd.read_csv("https://storage.googleapis.com/covid19-open-data/v2/weather.csv")

cl = pd.read_csv("https://raw.githubusercontent.com/prabodhw96/PRC/master/countries.csv")
cl = list(cl["Country"])

convert_dict = {"key": str}
weather = weather.astype(convert_dict)
weather = weather[~weather.key.str.contains("_")]
weather.key.dropna(inplace=True)

weather = weather.drop(columns=["noaa_station", "noaa_distance"])

weather = weather.sort_values(by=["key", "date"]).reset_index(drop=True)
weather = weather[~weather.key.str.contains("nan")]

import pycountry
names = {}
count = 0
for i in list(weather.key):
    if pycountry.countries.get(alpha_2=i) is None:
        continue
    names[i] = pycountry.countries.get(alpha_2=i).name
    count += 1

names["AN"] = "Netherlands Antilles"
names["XK"] = "Kosovo"
names["GZ"] = "Gaza Strip"

weather["key"].replace(names, inplace=True)

typo = ["Brunei Darussalam", "Syrian Arab Republic", "Tanzania, United Republic of", "Viet Nam", "Côte d'Ivoire", "Czechia",
       "Korea, Democratic People's Republic of", "Iran, Islamic Republic of", "Russian Federation",
       "Bolivia, Plurinational State of", "Lao People's Democratic Republic", "Korea, Republic of", "Slovakia",
       "Taiwan, Province of China", "Venezuela, Bolivarian Republic of"]
fix = ["Brunei", "Syria", "Tanzania", "Vietnam", "Cote d'Ivoire", "Czech Republic", "North Korea", "Iran", "Russia", "Bolivia",
      "Laos", "South Korea", "Slovak Republic", "Taiwan", "Venezuela"]

correct = dict(zip(typo, fix))
weather.key.replace(correct, inplace=True)

na_countries = []
for i in list(weather.key):
    if i not in cl:
        na_countries.append(i)

na_countries = list(set(na_countries))

weather_updated = weather[~weather.key.isin(na_countries)]

import base64

def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

if st.button('Download weather data'):
    tmp_download_link = download_link(weather_updated, 'weather.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)