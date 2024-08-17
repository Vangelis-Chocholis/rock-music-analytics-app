import streamlit as st
import plotly.graph_objs as go
#import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from functions import show_artists_table




def artist_trend_line(selected_artists, key_word='artist_popularity'):
    # Create a list to store the trend line traces
    trend_line_traces = []
    
    # Iterate over the selected artists
    for index, artist in selected_artists.iterrows():
        # Create a trend line trace for each artist
        trend_line_trace = go.Scatter(
            x = [date for date, _ in artist[f'date_{key_word}_list']],
            y = [popularity for _, popularity in artist[f'date_{key_word}_list']],
            mode = 'lines',
            name = artist['artist_name']
        )
        # Add the trend line trace to the list
        trend_line_traces.append(trend_line_trace)
    
    # Create the trend line plot layout
    if key_word == 'artist_popularity':
        trend_line_layout = go.Layout(
            title = 'Artist Popularity Trend',
            xaxis_title = 'Date',
            yaxis_title = 'Popularity',
            showlegend = True,
            yaxis=dict(
                title='Popularity',
                range=[0, 100]
            )
        )
    elif key_word == 'followers':
        trend_line_layout = go.Layout(
            title = 'Artist Followers Trend',
            xaxis_title = 'Date',
            yaxis_title = 'Followers',
            showlegend = True,
            yaxis=dict(
                title='Followers',
                #range=[0, 1000000]
            )
        )
    
     # Create the trend line plot figure
    trend_line_fig = go.Figure(data=trend_line_traces, layout=trend_line_layout)
    
    return trend_line_fig


#############################
# App page


st.title("🧑🏽‍🎤 Artists")

# Load the cached data
artists_data = st.session_state['cached_artist_data']
artists_data = artists_data.sort_values(by='current_artist_popularity', ascending=False)

# add a chart column to select artists to be displayed in the charts
artists_data['chart'] = False
artists_data.loc[artists_data.index[0], 'chart'] = True


# Add a checkbox to unselect all 'Chart' ticks
clear_charts_button = st.button('Unselect all artists')
if clear_charts_button:
    artists_data['chart'] = False

#   display the artists table
artists_data = show_artists_table(artists_data)

# Filter the selected artists to show in the charts
selected_artists = artists_data[artists_data['chart']]



tab1, tab2, tab3 = st.tabs(["Current Artist Popularity & Followers", "Artist Popularity Trend", "Artist Followers Trend"])
with tab2:
    st.plotly_chart(artist_trend_line(selected_artists, key_word='artist_popularity'), use_container_width=True)
with tab3:
    st.plotly_chart(artist_trend_line(selected_artists, key_word='followers'), use_container_width=True)
with tab1:
    artists_data_shorted = artists_data.sort_values(by='current_followers', ascending=False)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Step 4: Add Bar for 'current_followers'
    fig.add_trace(go.Bar(
        x=[x + 0.1 for x in range(len(artists_data_shorted['artist_name']))],  # Adjust x to avoid overlap
        y=artists_data_shorted['current_followers'],
        name='Followers',
        marker_color='rgba(255, 167, 38, 0.6)',
        width=0.25,  # Adjust the width of the bars
    ), secondary_y=False)

    # Add Bar for 'current_artist_popularity'
    fig.add_trace(go.Bar(
        x=[x - 0.2 for x in range(len(artists_data_shorted['artist_name']))],  # Adjust x to avoid overlap
        y=artists_data_shorted['current_artist_popularity'],
        name='Popularity',
        marker_color='rgba(30, 136, 229, 0.6)',
        width=0.25,  # Adjust the width of the bars
    ), secondary_y=True)

    # Step 5: Adjust layout for dual y-axes and other aesthetics
    fig.update_layout(
        title='Current Artist Popularity & Followers on Spotify',
        xaxis=dict(
            title='Artist',
            tickvals=list(range(len(artists_data_shorted['artist_name']))),
            ticktext=artists_data_shorted['artist_name'],
            tickangle=-65
        ),
        yaxis=dict(
            title='Followers',
        ),
        yaxis2=dict(
            title='Popularity',
            overlaying='y',
            side='right',
        ),
        barmode='group',
        legend=dict(
            x=1,  # Adjust this value between 0 and 1 to move the legend along the x-axis
            y=1,  # Adjust this value between 0 and 1 to move the legend along the y-axis
            xanchor='right',  # Anchor point of the legend. Use 'left' or 'right'
            yanchor='bottom',  # Anchor point of the legend. Use 'top' or 'bottom'
        )
    )
    fig.update_yaxes(showgrid=False ,secondary_y=True)
        
    #fig.update_yaxes(showgrid=False, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    
