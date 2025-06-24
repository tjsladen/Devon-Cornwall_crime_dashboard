# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 10:22:20 2025

@author: tjsla
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

# ----- Page Config -----
st.set_page_config(page_title="Crime Trends Across Devon and Cornwall", layout="wide")
st.title("Explore crime in Devon and Cornwall by LSOA from 2022-2025.")
st.markdown("""This dashboard explores crime in Devon and Cornwall.
            Use the tools bellow to explore.""")

@st.cache_data
def load_total_count_data():
    df = pd.read_parquet(r"C:\Users\tjsla\OneDrive\Desktop\Personal projects\crime dashboard\scripts_data\crime_counts.parquet")
    return df

def load_count_type():
    df = pd.read_parquet(r"C:\Users\tjsla\OneDrive\Desktop\Personal projects\crime dashboard\scripts_data\crime_type_counts.parquet")
    return df

def load_outcomes():
    df = pd.read_parquet(r"C:\Users\tjsla\OneDrive\Desktop\Personal projects\crime dashboard\scripts_data\outcomes.parquet")
    return df

def load_GeoJSON():
    gdf = gpd.read_file(r"C:\Users\tjsla\OneDrive\Desktop\Personal projects\crime dashboard\scripts_data\reduced.geojson")
    return gdf

count_df = load_total_count_data()
count_df["Month"] = count_df["Month"].dt.to_timestamp()
count_df['Year'] = count_df['Month'].dt.year
yearly_crime = count_df.groupby(['LSOA code', 'LSOA name', 'Year'], as_index=False)['Crime Count'].sum()

count_type_df = load_count_type()
outcomes_df = load_outcomes()
gdf = load_GeoJSON()
gdf = gdf.rename(columns={"LSOA21CD": "LSOA code"})
gdf = gdf.rename(columns={"LSOA21NM": "LSOA name"})

# ----- Sidebar -----
st.sidebar.title("Sidebar Options")

selected_year = st.sidebar.slider(
    "Select Overview/Crime Map Year", 
    int(count_type_df["Year"].min()), 
    int(count_type_df["Year"].max()), 
    step=1,
    value=int(count_df["Year"].max())
)

selected_lsoa = st.sidebar.selectbox(
    "Select LSOA for Overview",
    count_type_df["LSOA name"]
)

# ----- Overview -----

st.header("Area Overview")

# Filter data for selected LSOA and year
lsoa_data = count_type_df[
    (count_type_df["LSOA name"] == selected_lsoa) &
    (count_type_df["Year"] == selected_year)
]

# Group by crime type and calculate total counts
crime_summary = (
    lsoa_data.groupby("Crime type")["Crime Count"]
             .sum()
             .reset_index()
             .sort_values(by="Crime Count", ascending=False)
)

# If there's no crime data, show a message
if crime_summary.empty:
    st.subheader(f"No crime data available for {selected_lsoa} in {selected_year}.")
else:
    # Total crimes in the LSOA that year
    total_crimes = crime_summary["Crime Count"].sum()

    # Get most and least common
    most_common = crime_summary.iloc[0]

    # Calculate percentages
    most_pct = (most_common["Crime Count"] / total_crimes) * 100

    # Display results
    st.subheader(f"{selected_lsoa} - Most Prevalent Crime ({selected_year})")
    st.markdown(
        f"🔍 In **{selected_lsoa}**, the most prevalent crime type in {selected_year} was "
        f"**{most_common['Crime type']}**, making up **{most_pct:.1f}%** of all crimes."
    )

# ----- Map -----
st.subheader("🗺️ Crime Map by LSOA")

gdf_map = gdf.merge(yearly_crime, on="LSOA code")

# Filter for selected year
gdf_map = gdf_map[gdf_map["Year"] == selected_year]

custom_bins = [0, 10, 50, 100, 200, 500, 1000, 1830]
bin_labels = ['0–9', '10–49', '50–99', '100–199', '200–499', '500–999', '1000–1830']

gdf_map['Crime Bin'] = pd.cut(
    gdf_map['Crime Count'],
    bins=custom_bins,
    labels=bin_labels,
    include_lowest=False
)


# Plot the choropleth
fig = px.choropleth(
    gdf_map,
    geojson=gdf_map.geometry.__geo_interface__,
    locations=gdf_map.index,
    color="Crime Bin",
    hover_name="LSOA name_x",
    hover_data={"Crime Count": True},
    projection="mercator",
    category_orders={"Crime Bin": bin_labels},
    color_discrete_sequence=px.colors.sequential.Blues,
    labels={"Crime Bin": "Crime Count Range"}
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)

# ----- TimeSeries -----
st.subheader("📈 Crime Over Time by LSOA")

# Multiselect to compare up to two LSOAs
selected_lsoas = st.multiselect(
    "Select up to 2 LSOAs to compare:",
    options=sorted(count_df["LSOA name"].unique()),
    default=[count_df["LSOA name"].unique()[0]],
    max_selections=2
)

# Filter data
ts_df = count_df[count_df["LSOA name"].isin(selected_lsoas)].sort_values("Month")

# Check if there's data to plot
if not ts_df.empty and len(selected_lsoas) > 0:
    fig_trend = px.line(
        ts_df,
        x="Month",
        y="Crime Count",
        color="LSOA name",
        title="Crime Trend Comparison",
        labels={"Month": "Year","Crime Count": "Crime Count", "LSOA name": "LSOA"},
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Please select at least one LSOA to display the trend.")

# ----- PieChart Type-----
st.subheader("Crime Count Types by LSOA")

# Sidebar or section selectors
selected_year_ct = st.selectbox("Select Year for Crime Type Chart", sorted(count_type_df["Year"].unique()))
selected_lsoa_ct = st.selectbox("Select LSOA for Crime Type Chart", sorted(count_type_df["LSOA name"].unique()))

filtered_ct = count_type_df[
    (count_type_df["Year"] == selected_year_ct) &
    (count_type_df["LSOA name"] == selected_lsoa_ct)
]

if filtered_ct.empty:
    st.info(f"No outcome data for {selected_lsoa_ct} in {selected_year_ct}.")
else:
    pie_fig_ct = px.pie(
        filtered_ct,
        values="Crime Count",
        names="Crime type",
        title=f"Crime Type Distribution for {selected_lsoa_ct} ({selected_year_ct})",
    )
    pie_fig_ct.update_traces(textposition='inside', textinfo='value+label')
    st.plotly_chart(pie_fig_ct, use_container_width=True)   
# ----- PieChart Outcome-----
st.subheader("Crime Outcomes by LSOA")

# Sidebar or section selectors
selected_year_outcome = st.selectbox("Select Year for Outcome Chart", sorted(outcomes_df["Year"].unique()))
selected_lsoa_outcome = st.selectbox("Select LSOA for Outcome Chart", sorted(outcomes_df["LSOA name"].unique()))

# Filter the data
filtered_outcome = outcomes_df[
    (outcomes_df["Year"] == selected_year_outcome) &
    (outcomes_df["LSOA name"] == selected_lsoa_outcome)
]

# Check for data
if filtered_outcome.empty:
    st.info(f"No outcome data for {selected_lsoa_outcome} in {selected_year_outcome}.")
else:
    pie_fig = px.pie(
        filtered_outcome,
        values="Count",
        names="Last outcome category",
        title=f"Outcome Distribution for {selected_lsoa_outcome} ({selected_year_outcome})",
    )
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(pie_fig, use_container_width=True)

# ----- Footer -----
st.markdown("---")
st.caption("""
Data sources: [UK Police Crime Data](https://data.police.uk/data/) and [ONS Geography Portal](https://geoportal.statistics.gov.uk/).  
This app uses processed data: police crime files were filtered, combined and aggregated by LSOA code and Month; map geometry was filtered to show only Cornwall and Devon.  
Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
""")