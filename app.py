import numpy as np
import pandas as pd
import pycountry
import base64
import streamlit as st

st.title("Data for XPrize")
st.markdown("Updated daily by 9:30 AM EST")

def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


cl = pd.read_csv("https://raw.githubusercontent.com/prabodhw96/PRC/master/countries.csv")
cl = list(cl["Country"])


st.markdown("**Oxford COVID-19 Government Response Tracker**")
oxford = pd.read_csv("https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv",
				parse_dates=['Date'], encoding="ISO-8859-1", dtype={"RegionName": str, "RegionCode": str}, error_bad_lines=False)

oxford['GeoID'] = oxford['CountryName'] + '__' + oxford['RegionName'].astype(str)

oxford['NewCases'] = oxford.groupby('GeoID').ConfirmedCases.diff().fillna(0)

id_cols = ['CountryName',
           'RegionName',
           'GeoID',
           'Date']

cases_col = ['NewCases']

npi_cols = ['C1_School closing',
            'C2_Workplace closing',
            'C3_Cancel public events',
            'C4_Restrictions on gatherings',
            'C5_Close public transport',
            'C6_Stay at home requirements',
            'C7_Restrictions on internal movement',
            'C8_International travel controls',
            'H1_Public information campaigns',
            'H2_Testing policy',
            'H3_Contact tracing',
            'H6_Facial Coverings']

oxford = oxford[id_cols + cases_col + npi_cols]

oxford.update(oxford.groupby('GeoID').NewCases.apply(lambda group: group.interpolate()).fillna(0))

for npi_col in npi_cols:
    oxford.update(oxford.groupby('GeoID')[npi_col].ffill().fillna(0))

countries = list(oxford.groupby("CountryName").count().index)

oxford = oxford[['Date', 'CountryName', 'RegionName', 'GeoID', 'NewCases',
       'C1_School closing', 'C2_Workplace closing', 'C3_Cancel public events',
       'C4_Restrictions on gatherings', 'C5_Close public transport',
       'C6_Stay at home requirements', 'C7_Restrictions on internal movement',
       'C8_International travel controls', 'H1_Public information campaigns',
       'H2_Testing policy', 'H3_Contact tracing', 'H6_Facial Coverings']]

#oxford.to_csv("oxford_xprize.csv", index=False)
if st.button('Download OxCGRT latest data'):
    tmp_download_link = download_link(oxford, 'oxford_xprize.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.markdown("**ECDC COVID-19**")
ecdc = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/full_data.csv")

ecdc = ecdc[["date", "location", "new_cases"]]

ecdc.rename(columns={"location":"country"}, inplace=True)

countries = set(list(ecdc.groupby("country").count().index))

common_countries = list(set(cl) & set(countries))
common_countries.sort()

na_countries = []
for i in countries:
    if i not in cl:
        na_countries.append(i)

ecdc_common = ecdc[ecdc["country"].isin(common_countries)].sort_values(by=["country", "date"])
#ecdc_common.to_csv("ecdc_new_cases.csv", index=False)
if st.button('Download ECDC Data'):
    tmp_download_link = download_link(ecdc_common, 'ecdc_new_cases.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.markdown("**Google Mobility Trends (2020)**")
gmobility = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/gmobility/Google%20Mobility%20Trends%20(2020).csv")

date_encoded = gmobility[gmobility["Country"]=="India"]["Year"].value_counts().index.tolist()
date_encoded.sort()

import datetime

dates = [datetime.datetime(2020, 2, 15) + datetime.timedelta(days=x) for x in range(len(date_encoded))]
dates = [x.date().strftime('%Y-%m-%d') for x in dates]

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

date_dict = dict(zip(unique(date_encoded), dates)) 

gmobility.replace({"Year": date_dict}, inplace=True)

#gmobility.to_csv("gmobility.csv", index=False)
if st.button('Download Google Mobility data'):
    tmp_download_link = download_link(gmobility, 'gmobility.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.markdown("**OWID-COVID-19**")
owid = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")

locations = list(owid.groupby("location").count().index)

na_countries = []
count = 0
for i in locations:
    if i in cl:
        count += 1
    else:
        na_countries.append(i)

owid_179 = owid[~owid["location"].isin(na_countries)]
#owid_179.to_csv("owid-covid-data-179.csv", index=False)
if st.button('Download OWID-COVID-19 data (179 countries)'):
    tmp_download_link = download_link(owid_179, 'owid-covid-data-179.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


owid_world = owid[owid["location"]=="World"]
#owid_world.to_csv("owid-covid-data-world.csv", index=False)
if st.button('Download OWID-COVID-19 data (World)'):
    tmp_download_link = download_link(owid_world, 'owid-covid-data-world.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.markdown("**COVID-19 Testing**")
testing = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-all-observations.csv")

testing.drop(columns=["ISO code", "Source label"], inplace=True)
testing.rename(columns={"Entity":"Country"}, inplace=True)

testing["Country"] = testing["Country"].str.split("-", n = 1, expand = True)[0].str.strip()

countries = list(testing.groupby("Country").count().index)

na_countries = []
for i in cl:
    if i not in list(testing["Country"]):
        na_countries.append(i)

#testing.to_csv("covid-tests-performed.csv", index=False)
if st.button('Download COVID-19 Testing data'):
    tmp_download_link = download_link(owid_world, 'owid_world.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.markdown("**Human Capital Index - September 2020**")
hci = pd.read_excel("https://raw.githubusercontent.com/prabodhw96/PRC/master/data/hci_data_september_2020.xlsx", sheet_name="HCI 2020 - MaleFemale")

hci = hci[["Country Name", "Income Group", "HUMAN CAPITAL INDEX 2020"]]

hci.rename(columns={"Country Name":"Country", "Income Group":"Income_Group", "HUMAN CAPITAL INDEX 2020":"HCI"}, inplace=True)

na_countries = []
for i in cl:
    if i not in list(hci["Country"]):
        na_countries.append(i)

in_hci = ['Brunei Darussalam', 'Congo, Rep.', "'Congo, Dem. Rep.'", "Côte d'Ivoire", 'Egypt, Arab Rep.', "Hong Kong SAR, China", 
            "Iran, Islamic Rep.", 'Macao SAR, China', 'Russian Federation', 'Yemen, Rep.']
in_countries = ['Brunei', 'Congo', "Democratic Republic of Congo", "Cote d'Ivoire", "Egypt", "Hong Kong", "Iran", "Macao", "Russia", "Yemen"]

fix_names = dict(zip(in_hci, in_countries))

hci = hci.replace(fix_names)

na_c1 = []
for i in list(hci["Country"]):
    if i not in countries:
        na_c1.append(i)

hci_c = hci[~hci.Country.isin(na_c1)]

#hci_c.to_csv("hci_sep_2020.csv", index=False)
if st.button('Download HCI data'):
    tmp_download_link = download_link(hci_c, 'hci_c.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


st.markdown("**Health data**")
health = pd.read_csv("https://storage.googleapis.com/covid19-open-data/v2/health.csv")

convert_dict = {"key": str}
health = health.astype(convert_dict)

health = health[~health.key.str.contains("_")]
health = health[~health.key.str.contains("nan")]

names = []
for i in list(health.key):
    if i is None:
        continue
    names.append(pycountry.countries.get(alpha_2=i).name)

health["key"] = names

typo = ["Brunei Darussalam", "Congo, The Democratic Republic of the", "Côte d'Ivoire", "Czechia", "Iran, Islamic Republic of",
        "Korea, Republic of", "Moldova, Republic of", "Palestine, State of", "Russian Federation", "Slovakia", 
        "Syrian Arab Republic", "Tanzania, United Republic of", "Viet Nam"]
fix = ["Brunei", "Democratic Republic of Congo", "Cote d'Ivoire", "Czech Republic", "Iran", "South Korea", "Moldova", 
       "Palestine", "Russia", "Slovak Republic", "Syria", "Tanzania", "Vietnam"]

correct = dict(zip(typo, fix))
health.key.replace(correct, inplace=True)

na_countries = []
for i in list(health.key):
    if i not in cl:
        na_countries.append(i)

health_updated = health[~health.key.isin(na_countries)]
#health_updated.to_csv("health.csv", index=False)
if st.button('Download Health data'):
    tmp_download_link = download_link(health_updated, 'health_updated.csv', 'Click here to download')
    st.markdown(tmp_download_link, unsafe_allow_html=True)