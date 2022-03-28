import pandas as pd
import altair as alt
import streamlit as st

@st.cache
def loadData():
    return pd.read_csv('/Users/rossguthery/Desktop/chocoloate.csv')

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

if __name__ == '__main__':
	# Load in data.
	df = loadData()

	# Create a new dataframe that contains bean use counts.
	df_bean_use_counts = df.groupby('country_bean_origin').count()

	# Create filters.
	list_bean_prods  = set(df['country_bean_origin'])
	first_bean_prod  = st.sidebar.selectbox('Select first bean producer:', list_bean_prods)
	second_bean_prod = st.sidebar.selectbox('Select second bean producer:', list_bean_prods)
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
