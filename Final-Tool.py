import pandas as pd
import altair as alt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load cleaned version of base dataset.
@st.cache
def loadData():
	return pd.read_csv('Chocolate-Data-Set-Cleaned.csv')

# Load first dataset needed for the first sub-component.
@st.cache
def loadContinent():
	return pd.read_csv('Countries-Continents.csv')

# Load second dataset needed for the first sub-component.
@st.cache
def loadGeo():
	return pd.read_csv('Geo-Data.csv', sep = '\t', header = None, names = ['pop_est', 'continent', 'name', 'iso_a3',
	                                                                       'gdp_md_est', 'geometry', 'avg_rating'])

# Load image needed for the first sub-component.
@st.cache
def loadImage():
	return 'map.png'

# Load dataset needed for the third sub-component.
@st.cache
def loadStar():
	return pd.read_csv('Star-Chart-Data.csv')

@st.cache(allow_output_mutation = True)
def ingredients_ratings_chart(df, key):
	if len(key) > 0:
		df = df[df['country_bean_origin'] == key]

	base = alt.Chart(df)

	# Create a multi-select tool.
	multi_select = alt.selection_multi(toggle = False, empty = 'all', nearest = True)

	# Create a scatter plot of bar counts by number of ingredients used and rating.
	scatter = base.mark_point().encode(
			x = alt.X('num_ingredients:Q', title = 'Num. ingredients', scale = alt.Scale(domain = [0, 6])),
			y = alt.Y('rating:Q', title = 'Rating'),
			size = alt.Size('count():Q', legend = alt.Legend(title = 'Observations')),
			tooltip = [alt.Tooltip('num_ingredients:Q', title = 'Num. ingredients'),
			           alt.Tooltip('rating:Q', title = 'Rating'),
			           alt.Tooltip('count():Q', title = 'Bar count')],
			color = alt.condition(multi_select, alt.value('darkblue'), alt.value('lightgray'))
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

def update(liste, coef):
	return [elt * coef for elt in liste]

@st.cache(allow_output_mutation = True)
def star_chart(df, key1, key2):
	country_1 = key1
	country_2 = key2
	countries = [country_1, country_2]

	# Filter the dataframe according to these countries.
	df_countries_filtered = df[df.country_bean_origin.isin(countries)]

	# Keep the needed columns and group by country to get averaged values.
	df_countries_filtered = df_countries_filtered[["country_bean_origin", "salt", "lecithin", "sugar", "vanilla",
	                                               "cocoa_butter", "sweetener_other"]].groupby(
		"country_bean_origin").mean()

	# Store values in a list.
	list_countries = df_countries_filtered.to_numpy().tolist()
	country_1_values = update(list_countries[0], 100)
	country_2_values = update(list_countries[1], 100)

	# Get averages by continent.
	continent_1 = continents.loc[continents['Country'] == country_1, 'Continent'].iloc[0]
	continent_2 = continents.loc[continents['Country'] == country_2, 'Continent'].iloc[0]
	continents_list = [continent_1, continent_2]

	# Filter the dataframe according to these continents.
	df_continents_filtered = df[df.continent.isin(continents_list)]

	# Keep the needed columns and group by continent to get averaged values.
	df_continents_filtered = df_continents_filtered[
		["continent", "salt", "lecithin", "sugar", "vanilla", "cocoa_butter",
		 "sweetener_other"]].groupby("continent").mean()

	# Usable values.
	list_continents = df_continents_filtered.to_numpy().tolist()
	continents_1_values = update(list_continents[0], 100)

	if len(list_continents) > 1:
		continents_2_values = update(list_continents[1], 100)
	else:
		continents_2_values = continents_1_values

	fig = make_subplots(rows = 1, cols = 2, specs = [[{'type': 'polar'}] * 2])
	categories = ["Salt", "Lecithin", "Sugar", "Vanilla", "Cocoa butter", "Other sweetener"]

	fig.add_trace(go.Scatterpolar(
			r = country_1_values,
			theta = categories,
			fill = 'toself',
			name = country_1
	)
	)

	fig.add_trace(go.Scatterpolar(
			r = continents_1_values,
			theta = categories,
			fill = 'none',
			name = f'{continent_1} avg.'
	)
	)

	fig.add_trace(go.Scatterpolar(
			r = country_2_values,
			theta = categories,
			fill = 'toself',
			name = country_2,
			subplot = 'polar2'
	), 1, 2)

	fig.add_trace(go.Scatterpolar(
			r = continents_2_values,
			theta = categories,
			fill = 'none',
			name = f'{continent_2} avg.',
			subplot = 'polar2'
	), 1, 2)

	fig.update_polars()

	fig.update_layout(
			title = dict(
				text = f'<b>Average Ingredient Usage</b> for Bars Made With Beans From <b>{country_1}</b> and <b>{country_2}</b>',
				xref = 'container', x = 0.5),
			polar = dict(
					radialaxis = dict(
							visible = True,
							range = [0, 100]
					)
			),
			polar2 = dict(
					radialaxis = dict(
							visible = True,
							range = [0, 100]
					)
			),
			showlegend = True,
			legend = dict(orientation = 'h', xanchor = 'auto', yanchor = 'auto', x = 0.5)
	)

	return fig

@st.cache(allow_output_mutation = True)
def geo_chart(df):
	fig = go.Figure(data = go.Choropleth(
			locations = geo_df['iso_a3'],
			z = geo_df['avg_rating'],
			text = geo_df['name'],
			colorscale = 'blues',
			autocolorscale = False,
			reversescale = False,
			marker_line_color = 'darkgray',
			marker_line_width = 0.5,
			zmin = geo_df.avg_rating.min(),
			zmax = geo_df.avg_rating.max(),
			colorbar_title = '<b>Avg. rating</b>',
	)
	)

	fig.update_layout(
			title_text = '<b>Average Bar Ratings</b> by <b>Cocoa Producing Country</b>',
			geo = dict(landcolor = 'whitesmoke',
			           showland = True,
			           showcountries = True,
			           countrycolor = 'whitesmoke',
			           showframe = False,
			           showcoastlines = False,
			           projection_type = 'equirectangular'
			           )
	)

	return fig

if __name__ == '__main__':
	# Load data.
	df = loadData()
	geo_df = loadGeo()
	world_map = loadImage()
	star_df = loadStar()
	continents = loadContinent()

	# Title our visualization.
	st.write('# The Lifecycle of a Chocolate Bar')

	# Title the first sub-component.
	st.write('### Which Countries Grow Cocoa?')

	# Put the first sub-component into context.
	st.write("Cocoa beans, a critical ingredient in chocolate bars, are grown in countries around the world, "
	         "particularly in those that are at or near the equator. Just because many countries grow beans, however, "
	         "does not mean that bars made from beans of different origins will taste or be rated the same. "
	         "The map below shows how average ratings of chocolate bars vary across cocoa bean producing countries.")

	# Plot the first sub-component.
	st.plotly_chart(geo_chart(geo_df))

	# Title the second sub-component.
	st.write("### Does the Number of Ingredients Affect a Bar's Rating?")

	# Put the second sub-component into context.
	st.write("After cocoa beans are harvested and fermented, they often get mixed with one or several ingredients "
	         "before being turned into, packaged, and sold as chocolate bars. One potential explanation for the variation "
	         "observed in the map above is therefore that the number of ingredients cocoa beans get mixed with during "
	         "production is correlated with where said cocoa beans come from, which in turn affects the rating the final "
	         "bar receives. Of course, a country may have one superb bar made from its beans while another has many "
	         "mediocre bars made from its. Hence our displaying bar counts in the plots below.")

	st.write('###### Focus on two countries by selecting them in the sidebar.')

	# Create a new dataframe that contains bean use counts.
	df_bean_use_counts = df.groupby('country_bean_origin').count()

	# Create filters.
	list_bean_prods = set(df['country_bean_origin'])
	first_bean_prod = st.sidebar.selectbox('Select first bean producer:', list_bean_prods, index = 2)
	second_bean_prod = st.sidebar.selectbox('Select second bean producer:', list_bean_prods, index = 10)
	keys = {'bean_prod_1': first_bean_prod, 'bean_prod_2': second_bean_prod}

	# Display filter above first chart.
	st.write(f'##### First Bean Producer: _{first_bean_prod}_')

	# Create first chart.
	st.altair_chart(ingredients_ratings_chart(df, keys['bean_prod_1']))

	# Display total bar count below first chart.
	text_subtitle = st.empty()
	count_1 = df_bean_use_counts['rating'].loc[first_bean_prod]
	text_subtitle.markdown(f'Their beans were used in **{count_1}** bars.')

	# Display filter above second chart.
	st.write(f'##### Second Bean Producer: _{second_bean_prod}_')

	# Create second chart.
	st.altair_chart(ingredients_ratings_chart(df, keys['bean_prod_2']))

	# Display total bar count below second chart.
	text_subtitle = st.empty()
	count_2 = df_bean_use_counts['rating'].loc[second_bean_prod]
	text_subtitle.markdown(f'Their beans were used in **{count_2}** bars.')

	# Title the third sub-component.
	st.write('### Which Ingredient Pairings Are Most Common?')

	# Put the third sub-component into context.
	st.write("The plots above take a look at the number of ingredients being used, but they do not take into account "
	         "which ingredients are being used. Another possible explanation for the variation observed in the map "
	         "above is that certain combinations of ingredients are most capable of achieving the highest ratings. Plus,"
	         "ingredient combinations may also be correlated with the origin of the cocoa beans beings used. The star"
	         "charts allow the user to investigate this herself for the two countries selected in sidebar.")

	# Create star charts.
	st.plotly_chart(star_chart(df, keys['bean_prod_1'], keys['bean_prod_2']))