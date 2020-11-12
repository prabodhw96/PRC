import numpy as np
import pandas as pd
import pycountry
import streamlit as st

weather = pd.read_csv("https://storage.googleapis.com/covid19-open-data/v2/weather.csv")

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

weather_updated.to_csv("weather.csv", index=False)