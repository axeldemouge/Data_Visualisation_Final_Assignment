# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 15:14:40 2022

@author: hugov
"""
import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import geopandas as gpd
#from dataprep.clean import clean_country
#from altair import datum
#from vega_datasets import data
#from streamlit_vega_lite import vega_lite_component, altair_component
#import time

st.write('# Chocolate Bars Ratings')

st.write('## 1. Geographical Display')
# Load Gapminder data
# @st.cache decorator skip reloading the code when the apps rerun.
@st.cache
def loadData():
    return pd.read_csv('Chocolate-Data-Set-Cleaned.csv')

df = loadData()

@st.cache
def loadStar():
    return pd.read_csv('Star_chart_data.csv')

@st.cache
def loadContinent():
    return pd.read_csv('continents.csv')

@st.cache
def loadGeo():
    return pd.read_csv('geo_data.csv')

geo_df = loadGeo()
star_df = loadStar()
continents = loadContinent()


@st.cache(allow_output_mutation = True)
def ingredients_ratings_chart(df, key):
	if len(key) > 0:
		df = df[df['country_bean_origin'] == key]

	base = alt.Chart(df)

	# Create a multi-select tool.
	multi_select = alt.selection_multi(toggle = False, empty = 'all', nearest = True)

	# Create a scatter plot of bar counts by number of ingredients used and rating.
	scatter = base.mark_point().encode(
	    x       = alt.X('num_ingredients:Q', title  = 'Num. ingredients', scale = alt.Scale(domain = [0, 6])),
	    y       = alt.Y('rating:Q',          title  = 'Rating'),
	    size    = alt.Size('count():Q',      legend = alt.Legend(title = 'Observations')),
		tooltip = [alt.Tooltip('num_ingredients:Q', title = 'Num. ingredients'),
		           alt.Tooltip('rating:Q',          title = 'Rating'),
		           alt.Tooltip('count():Q',         title = 'Bar count')],
		color   = alt.condition(multi_select, alt.value('darkblue'), alt.value('lightgray'))
	).add_selection(multi_select)
	# Remove hashtags below to add titles if needed later on.
	# .properties(
	#     title = {
	#         'text'    :'Do more ingredients lead to better ratings?',
	#         'subtitle':'Not always! Three-ingredient bars have the highest average.'
	#     }
	# )

	# Create a line graph of average rating per ingredient number category.
	mean = base.mark_line(color = 'darkorange', point = alt.OverlayMarkDef(color = 'darkorange')).encode(
	    x = 'num_ingredients:Q',
	    y = 'mean(rating):Q'
	)

	# Return the line graph of average ratings by category superimposed onto the scatter plot.
	return scatter + mean

def update(liste,coef):
    return [elt*coef for elt in liste]

@st.cache(allow_output_mutation = True)
def star_chart(df, key1, key2):
	country_1 = key1
	country_2 = key2
	countries = [country_1,country_2]
    #Filter the dataframe depending on these country
	df_countries_filtered = df[df.country_bean_origin.isin(countries)]
    #Keep the needed columns and groupby country to get averaged values
	df_countries_filtered = df_countries_filtered[["country_bean_origin","salt","lecithin","sugar","vanilla","cocoa_butter","sweetener_other"]].groupby("country_bean_origin").mean()
    #store values in a list
	list_countries = df_countries_filtered.to_numpy().tolist()
	country_1_values = update(list_countries[0],100)
	country_2_values = update(list_countries[1],100)
    
    #Get the average by continent 
	continent_1 = continents.loc[continents['Country'] == country_1, 'Continent'].iloc[0]
	continent_2 = continents.loc[continents['Country'] == country_2, 'Continent'].iloc[0]
	print(f"Continent 1 : {continent_1} , Continent 2 : {continent_2}")
	continents_list = [continent_1,continent_2]
    #Filter the dataframe depending on these country
	df_continents_filtered = df[df.continent.isin(continents_list)]
    #Keep the needed columns and groupby country to get averaged values
	df_continents_filtered = df_continents_filtered[["continent","salt","lecithin","sugar","vanilla","cocoa_butter","sweetener_other"]].groupby("continent").mean()
    #Usable values
	list_continents = df_continents_filtered.to_numpy().tolist()
	continents_1_values = update(list_continents[0],100)
	if len(list_continents)>1:
		continents_2_values = update(list_continents[1],100)
	else:
	   continents_2_values = continents_1_values
    
	fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'polar'}]*2])
	categories = ["Salt","Lecithin","Sugar","Vanilla","Cocoa Butter","Other Sweetener"]
    
    
	fig.add_trace(go.Scatterpolar(
	      r=country_1_values,
	      theta=categories,
	      fill='toself',
	      name=country_1
	))
	fig.add_trace(go.Scatterpolar(
	      r=continents_1_values,
	      theta=categories,
	      fill='none',
	      name=f'Average in {continent_1}'
	))
	
	fig.add_trace(go.Scatterpolar(
	      r=country_2_values,
	      theta=categories,
	      fill='toself',
	      name=country_2,subplot = "polar2"
	    ), 1, 2)
	fig.add_trace(go.Scatterpolar(
	      r=continents_2_values,
	      theta=categories,
	      fill='none',
	      name=f'Average in {continent_2}',subplot = "polar2"
	    ), 1, 2)
	
	
	
	fig.update_polars()
	fig.update_layout(
	  title=dict(text=f"Average use of sweeteners in chocolate bars from beans of {country_1} and {country_2}",xref='container',x=0.5),
	  polar=dict(
	    radialaxis=dict(
	      visible=True,
	      range=[0, 100]
	    )),
	    polar2 = dict(
	      radialaxis = dict(visible=True,
	      range = [0, 100]
	    )),
	  showlegend=True,
	    legend=dict(orientation ='h',xanchor='auto',yanchor='auto',x=0.1)
	)
	
	return fig
	
	
@st.cache(allow_output_mutation = True)
def geo_chart(df):
	geochart = alt.Chart(df).mark_geoshape().encode( 
	    color= alt.condition("datum.avg_rating == '0'", alt.value('whitesmoke'), alt.Color(field = "avg_rating",type = "quantitative",
	                    scale= alt.Scale(domain=[2.86 , df.avg_rating.max()], scheme='browns', type = 'linear'), legend=alt.Legend(title="Rating",labelFontSize = 20,symbolSize = 20,titleFontSize=20))),
	    tooltip=[alt.Tooltip('name:N', title = 'Country bean producer'),
	             alt.Tooltip('avg_rating:Q', title= 'Average rating')]
	).properties(
	    title='Countries chocolate beans average rating',
	    projection={"type":'mercator'},
	    width=900,
	    height=500
	).configure_title(
	    fontSize=40,
	    align='center'
	)
	return geochart



    

if __name__ == '__main__':
	# Load in data.
	df = loadData()
	geo_df = loadGeo()
	
	#Plot Geo data
	st.altair_chart(geo_chart(geo_df))

	# Create a new dataframe that contains bean use counts.
	df_bean_use_counts = df.groupby('country_bean_origin').count()

	# Create filters.
	list_bean_prods  = set(df['country_bean_origin'])
	first_bean_prod  = st.sidebar.selectbox('Select first bean producer:', list_bean_prods, index = 2)
	second_bean_prod = st.sidebar.selectbox('Select second bean producer:', list_bean_prods, index = 10)
	keys             = {'bean_prod_1': first_bean_prod, 'bean_prod_2': second_bean_prod}

	# Display filter above first chart.
	text_title = st.empty()
	text_title.markdown(f'**First Bean Producer:** _{first_bean_prod}_')

	# Create first chart.
	st.altair_chart(ingredients_ratings_chart(df, keys['bean_prod_1']))

	# Display total bar count below first chart.
	text_subtitle = st.empty()
	count_1       = df_bean_use_counts['rating'].loc[first_bean_prod]
	text_subtitle.markdown(f'Their beans were used in **{count_1}** bars.')

	# Display filter above second chart.
	text_title = st.empty()
	text_title.markdown(f'**Second Bean Producer:** _{second_bean_prod}_')

	# Create second chart.
	st.altair_chart(ingredients_ratings_chart(df, keys['bean_prod_2']))

	# Display total bar count below second chart.
	text_subtitle = st.empty()
	count_2       = df_bean_use_counts['rating'].loc[second_bean_prod]
	text_subtitle.markdown(f'Their beans were used in **{count_2}** bars.')
    
    # Create Star Chart
	st.plotly_chart(star_chart(df, keys['bean_prod_1'], keys['bean_prod_2']))

