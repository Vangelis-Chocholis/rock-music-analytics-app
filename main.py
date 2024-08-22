import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
#import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
# access the functions from the 'streamlit_files' directory
#import sys
#sys.path.append('streamlit_files')
from connect_to_database import update_dynamic_tables




################################################
# Load the data
@st.cache_data
def load_static_data():
    """
    Load static data from CSV files.
    
    Returns:
        artists_table (pandas.DataFrame): DataFrame containing artist information.
        albums_table (pandas.DataFrame): DataFrame containing album information.
        tracks_table (pandas.DataFrame): DataFrame containing track information.
        tracks_features_table (pandas.DataFrame): DataFrame containing track features information.
    """
    artists_table = pd.read_csv('data/artists_table.csv')
    albums_table = pd.read_csv('data/albums_table.csv')
    tracks_table = pd.read_csv('data/tracks_table.csv')
    tracks_features_table = pd.read_csv('data/tracks_features_table.csv')
    return artists_table, albums_table, tracks_table, tracks_features_table


def process_date(table):
    """
    Converts the 'date' column in the given table to datetime format.
    
    Args:
        table (pandas.DataFrame): The table containing the 'date' column.
        
    Returns:
        pandas.DataFrame: The table with the 'date' column converted to datetime format.
    """
    table['date'] = pd.to_datetime(table['date'])
    return table


@st.cache_data
def load_dynamic_data():
    """
    Loads and processes dynamic data tables.

    This function updates the dynamic tables, processes the popularity tables for tracks, albums, artists, and followers,
    and returns the processed tables.

    Returns:
        tuple: A tuple containing the processed tables for tracks popularity, albums popularity, artists popularity, and artists followers.
    """
    updated_tables = update_dynamic_tables()
    tracks_popularity_table = process_date(updated_tables['tracks_popularity_table'])
    albums_popularity_table = process_date(updated_tables['albums_popularity_table'])
    artists_popularity_table = process_date(updated_tables['artists_popularity_table'])
    artists_followers_table = process_date(updated_tables['artists_followers_table'])
    return tracks_popularity_table, albums_popularity_table, artists_popularity_table, artists_followers_table


def merge_tracks_data(tracks_table, albums_table, artists_table, tracks_features_table):
    """
    Merges multiple tables to create a consolidated dataset. 

    Parameters:
    - tracks_table (pandas.DataFrame): The table containing information about tracks.
    - albums_table (pandas.DataFrame): The table containing information about albums.
    - artists_table (pandas.DataFrame): The table containing information about artists.
    - tracks_features_table (pandas.DataFrame): The table containing features of tracks.

    Returns:
    - data (pandas.DataFrame): The merged dataset containing information from all the input tables.
    """
    data = pd.merge(tracks_table, albums_table, on='album_id')
    data = pd.merge(data, artists_table[['artist_id', 'artist_name']], on='artist_id')
    data = pd.merge(data, tracks_features_table, on='track_id')
    return data


def get_popularity(popularity_table, key_word, artist_followers=False):
    """
    Groups the popularity table by `track_id` or `artist_id` and creates two new columns:
    1. `date_track_popularity_list` (or `date_artist_popularity_list`/`date_followers_list`): A list of tuples where each tuple
    contains a date and the corresponding popularity of the track/artist (or followers of the artist) on that date.
    2. `track_popularity_list` (or `artist_popularity_list`/`followers_list`): A list of popularity values for the 
    track/artist (or followers count for the artist) across different dates.

    Parameters:
    popularity_table : pd.DataFrame
        A DataFrame containing track or artist popularity information. It must include the columns `track_id`, `date`, 
        and `track_popularity` if `key_word='track'` and `artist_followers` is False,
        or `artist_id`, `date`, and `artist_popularity` if `key_word='artist'` and `artist_followers` is False, or `artist_id`,
        `date`, and `artist_followers` if `artist_followers` is True.
    key_word : str, optional
        The keyword to use for the column names, either 'track' or 'artist'.
    artist_followers : bool, optional
        If True, the function processes artist followers data. If False, it processes track or artist popularity data based on `key_word`. 
        Default is False.

    Returns:
    pd.DataFrame
        A DataFrame with the following columns:
        - `track_id` (or `artist_id`): The unique identifier for the track or artist.
        - `date_track_popularity_list` (or `date_artist_popularity_list`/`date_followers_list`): A list of tuples containing date and track/artist popularity (or followers).
        - `track_popularity_list` (or `artist_popularity_list`/`followers_list`): A list of track/artist popularity values (or followers count).
    """
    if not artist_followers:
        popularity_data = (popularity_table
                            .groupby(f'{key_word}_id')
                            .apply(lambda x: pd.Series({
                                f'date_{key_word}_popularity_list': list(zip(x['date'], x[f'{key_word}_popularity'])),
                                f'{key_word}_popularity_list': list(x[f'{key_word}_popularity'])
                            }), include_groups=False)
                            .reset_index()
                            )
    else:
        popularity_data = (popularity_table
                            .groupby('artist_id')
                            .apply(lambda x: pd.Series({
                                'date_followers_list': list(zip(x['date'], x['followers'])),
                                'followers_list': list(x['followers'])
                            }), include_groups=False)
                            .reset_index()
                            )
    return popularity_data


def process_tracks_data(data, tracks_popularity):
    """
    Process the given data by merging it with tracks_popularity, calculating the current track popularity,
    converting the mode values to 'major' or 'minor', and selecting the most popular track version for each 
    artist and track name.

    Args:
        data (pandas.DataFrame): The input data to be processed.
        tracks_popularity (pandas.DataFrame): The dataframe containing track popularity information.

    Returns:
        pandas.DataFrame: The processed data with the most popular track version for each artist and track name.
    """
    # Convert mode values to 'major' or 'minor'
    data['mode'] = np.where(data['mode'] == 1, 'major', 'minor')
    # we scale tempo to be between 0 and 1 for the radar chart
    data['tempo_scaled'] = (data['tempo'] - data['tempo'].min()) / (data['tempo'].max() - data['tempo'].min())
    # Merge the data with tracks popularity
    data = pd.merge(data, tracks_popularity, on='track_id')
    # Calculate the current track popularity
    data['current_track_popularity'] = data['track_popularity_list'].apply(lambda x: x[-1])
    # Select the most popular track version for each artist and track name
    data = (data
            .groupby(['artist_name', 'original_track_name'])
            .apply(lambda x: x.sort_values('current_track_popularity', ascending=False).head(1),
                include_groups=False)
            .reset_index(drop=False)
            .drop('level_2', axis=1)
            )
    # keep only the required columns
    data = data[['track_id', 'original_track_name', 'artist_name', 'album_image_medium', 
                                    'current_track_popularity', 'track_popularity_list', 'date_track_popularity_list',
                                    'track_spotify_url', 'track_preview_url', 'album_release_date',
                                    'acousticness', 'danceability', 'energy', 'instrumentalness', 'valence', 'tempo','mode', 'tempo_scaled']]
    return data


def process_artists_data(data, artists_popularity, artists_followers):
    # Merge the data with artists popularity and followers
    data = pd.merge(data, artists_popularity, on='artist_id')
    data = pd.merge(data, artists_followers, on='artist_id')
    # Calculate the current artist popularity and followers
    data['current_artist_popularity'] = data['artist_popularity_list'].apply(lambda x: x[-1])
    data['current_followers'] = data['followers_list'].apply(lambda x: x[-1])
    return data
    

@st.cache_data
def get_data():
    ''' Load, process, and merge static and dynamic music data tables.

    This function performs the following steps:
    1. Loads static data tables from CSV files.
    2. Loads dynamic data tables with updated information.
    3. Merges the static data tables into a single dataset.
    4. Aggregates and processes the tracks popularity data.
    5. Finalizes the dataset by integrating all data and retaining the most popular version of duplicate tracks.

    Returns:
    -------
    pd.DataFrame
        A DataFrame containing the merged and processed data with the following columns:
        - artist_id
        - album_id
        - track_id
        - original_track_name
        - mode
        - other columns from the static dat a tables
        - date_track_popularity_list: A list of tuples containing date and track popularity.
        - track_popularity_list: A list of track popularity values.
        - current_track_popularity: The latest popularity value for each track.
    '''
    # Load static data
    artists_table, albums_table, tracks_table, tracks_features_table = load_static_data()
    
    # Load dynamic data
    tracks_popularity_table, albums_popularity_table, artists_popularity_table, artists_followers_table = load_dynamic_data()
    
    # Merge static data for tracks
    tracks_data = merge_tracks_data(tracks_table, albums_table, artists_table, tracks_features_table)
    # Get tracks popularity data
    tracks_popularity = get_popularity(tracks_popularity_table, key_word='track')
    # Process the final dataset for tracks
    tracks_data = process_tracks_data(tracks_data, tracks_popularity)
    
    # Get artists popularity data and followers data
    artists_popularity = get_popularity(artists_popularity_table, key_word='artist')
    artists_followers = get_popularity(artists_followers_table, key_word='artist', artist_followers=True)
    # Process the final dataset for artists
    artists_data = process_artists_data(artists_table, artists_popularity, artists_followers) 
    
    # get mean track popularity over time
    mean_track_popularity_over_time = (tracks_popularity_table
         .groupby('date')
         .agg({'track_popularity': 'mean'})
         .reset_index()
         .rename(columns={'track_popularity': 'mean_track_popularity'})
         )
    
    return tracks_data, artists_data, mean_track_popularity_over_time


###########################################################
# testing w/o the use of database
@st.cache_data
def get_data1():
    data = pd.read_pickle('data/data.pkl')
    artists_data = pd.read_pickle('data/artists_data.pkl')
    tracks_popularity_table = pd.read_csv('data/tracks_popularity_table.csv')
    mean_track_popularity= (tracks_popularity_table
         .groupby('date')
         .agg({'track_popularity': 'mean'})
         .reset_index()
         .rename(columns={'track_popularity': 'mean_track_popularity'})
         )
    return data, artists_data, mean_track_popularity

####################################

# App Constuction
# import functions

from functions import * #show_tracks_table,write_features_description, track_features_scatter_plot



def main():
    st.title("🎸 Tracks")
    # get the data
    #Use get_data1() for testing without database, and get_data() for database connection
    data, artists_data, mean_track_popularity = get_data1()
    
    # save the data to pkl to avoid database connection
    #data.to_pickle('data/data.pkl')
    #artists_data.to_pickle('data/artists_data.pkl')
    
    # caching the data for use in other pages. 
    if 'cached_artist_data' not in st.session_state:
        st.session_state['cached_artist_data'] = artists_data

    # caching data for clustering page
    if 'cached_clustering_data' not in st.session_state:
        st.session_state['cached_clustering_data'] = data[['track_id', 'current_track_popularity']]
    
    st.sidebar.title('Filters')

    # dropdown to select the number of tracks to display
    n = int(st.sidebar.selectbox('Select the number of most popular tracks to display:', [10, 20, 50, 100, 250, 500, 1000, 1500, 2000, 2500, 3000, 5000]))
    
    
    
    # Get unique artists
    artists = data['artist_name'].sort_values().unique()

    # Add 'All' option to the list of artists
    artists = np.insert(artists, 0, 'All')

    # Multi-selection box for artists
    selected_artists = st.sidebar.multiselect('Select artists:', artists, default='All')

    # Filter data based on selected artists
    if 'All' in selected_artists:
        filtered_data = data
    elif len(selected_artists) == 0:
        st.warning('Please select at least one artist!')
        
    else:
        filtered_data = data[data['artist_name'].isin(selected_artists)]

    # select box for mode
    #mode = data['mode'].unique()

    # add 'All' option to the list of mode
    #mode = np.insert(mode, 0, 'All')

    # multi-selection box for mode
    #selected_mode = st.sidebar.selectbox('Select `Mode`:', mode)

    # filter data based on selected mode
    #if selected_mode == 'All':
    #    filtered_data = filtered_data
    #else:
    #    filtered_data = filtered_data[filtered_data['mode']==selected_mode]
    
    # slider for current popularity
    selected_popularity = st.sidebar.slider('Select Track Popularity Range:', value=[0, 100])
    

    st.sidebar.write('### Filter by Audio Features')
    # slider for tempo
    selected_tempo = st.sidebar.slider('Select `Tempo` BPM Range:', value=[data['tempo'].min(), data['tempo'].max()])
    
    # slider for energy
    selected_energy = st.sidebar.slider('Select `Energy` Range:', value=[0.0, 1.0])
    
    # slider for valence
    selected_valence = st.sidebar.slider('Select `Valence` Range:', value=[0.0, 1.0])
  
    # slider for danceability
    selected_danceability = st.sidebar.slider('Select `Danceability` Range:', value=[0.0, 1.0])
    
    # slider for acousticness
    selected_acousticness = st.sidebar.slider('Select `Acousticness` Range:', value=[0.0, 1.0])
    
    # slider for instrumentalness
    selected_instrumentalness = st.sidebar.slider('Select `Instrumentalness` Range:', value=[0.0, 1.0])
    
    # slider for album release date
    selected_release_date = st.sidebar.slider('Select `Album Release Date` Range:', value=[data['album_release_date'].min(), data['album_release_date'].max()],
                                              min_value=data['album_release_date'].min(), max_value=data['album_release_date'].max())

    # filter the data based on the slider values
    # current popularity
    filtered_data = filtered_data.query('current_track_popularity >= @selected_popularity[0] & current_track_popularity <= @selected_popularity[1]')
    # tempo
    filtered_data = filtered_data.query('tempo >= @selected_tempo[0] & tempo <= @selected_tempo[1]')
    # energy
    filtered_data = filtered_data.query('energy >= @selected_energy[0] & energy <= @selected_energy[1]')
    # valence
    filtered_data = filtered_data.query('valence >= @selected_valence[0] & valence <= @selected_valence[1]')
    # danceability
    filtered_data = filtered_data.query('danceability >= @selected_danceability[0] & danceability <= @selected_danceability[1]')
    # acousticness
    filtered_data = filtered_data.query('acousticness >= @selected_acousticness[0] & acousticness <= @selected_acousticness[1]')
    # instrumentalness
    filtered_data = filtered_data.query('instrumentalness >= @selected_instrumentalness[0] & instrumentalness <= @selected_instrumentalness[1]')
    # album release date
    filtered_data = filtered_data.query('album_release_date >= @selected_release_date[0] & album_release_date <= @selected_release_date[1]')    


    # filter the data for the selected number of tracks
    filtered_data = (filtered_data
                     .sort_values(by='current_track_popularity', ascending=False)
                     .reset_index(drop=True)
                     .head(n)
                     )
    
    # add a chart column to select tracks to be displayed in the charts
    filtered_data['chart'] = False
    filtered_data.loc[0, 'chart'] = True


    # Add a checkbox to unselect all 'Chart' ticks
    clear_charts_button = st.button('Unselect all tracks')
    if clear_charts_button:
        filtered_data['chart'] = False
    
    
    # display the table of the most popular tracks
    st.write(f"#### Top {n} Most Popular Tracks")    
    filtered_data = show_tracks_table(filtered_data)
    st.write('''Select the tracks to be displayed in the trend line plot by clicking on the **Chart** column in the table above.''')

    # Filter the data for selected tracks
    selected_tracks = filtered_data[filtered_data['chart']]
    
    # trend line plot for selected tracks
    def track_popularity_trend_line(selected_tracks):
        # Create a list to store the trend line traces
        trend_line_traces = []
        # Iterate over the selected tracks
        for index, track in selected_tracks.iterrows():
            # Create a trend line trace for each track
            trend_line_trace = go.Scatter(
                x = [date for date, _ in track['date_track_popularity_list']],
                y = [popularity for _, popularity in track['date_track_popularity_list']],
                mode = 'lines',
                name = track['original_track_name']
            )
            # Add the trend line trace to the list
            trend_line_traces.append(trend_line_trace)
            
        # Create the trend line trace for the average popularity
        mean_popularity_trace = go.Scatter(
        x=mean_track_popularity['date'],
        y=mean_track_popularity['mean_track_popularity'],
        mode='lines',  # Ensure that it's in line mode
        name='mean track popularity',  # Name the trace
        line=dict(
            dash='dot',  # Make the line dotted
            width=2, # Optional: Adjust the width of the line
            color='orange'
            )
        )
        trend_line_traces.append(mean_popularity_trace)
            
        # Create the trend line plot layout
        trend_line_layout = go.Layout(
            title = 'Track Popularity Trend',
            xaxis_title = 'Date',
            yaxis_title = 'Popularity',
            showlegend = True,
            yaxis=dict(
            title='Popularity',
            range=[0, 100]
            )
        )
        # Create the trend line plot figure
        trend_line_fig = go.Figure(data=trend_line_traces, layout=trend_line_layout)
        return trend_line_fig
    
    def radar_chart(selected_tracks):
        # Create a list to store the radar chart traces
        radar_traces = []
        # Iterate over the selected tracks
        for index, track in selected_tracks.iterrows():
            # Create a radar trace for each track
            radar_trace = go.Scatterpolar(
                r = [track['acousticness'], track['danceability'], track['valence'], track['energy'],  track['tempo_scaled'], track['instrumentalness']],
                theta = ['acousticness', 'danceability','valence', 'energy', 'tempo (scaled)', 'instrumentalness'],
                fill = 'toself',
                name = track['original_track_name']
            )
            # Add the radar trace to the list
            radar_traces.append(radar_trace)
        # Create the radar chart layout
        radar_layout = go.Layout(
            polar = dict(
                radialaxis = dict(
                    visible = True,
                    range = [0, 1]
                )
            ),
            showlegend = True,
            title='Track Features Radar Chart'
        )
        # Create the radar chart figure
        radar_fig = go.Figure(data=radar_traces, layout=radar_layout)
        return radar_fig

    
    
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Track Popularity Trend', 'Radar Chart', 'Track Features Description','Track Features Distribution', 'Track Counts by Artist'])
    with tab1:
        # display the trend line plot
        trend_line_fig = track_popularity_trend_line(selected_tracks)
        st.plotly_chart(trend_line_fig)
    with tab2:
        # display the radar chart
        radar_fig = radar_chart(selected_tracks)
        st.plotly_chart(radar_fig)
    with tab3:
        # description of the track features
        write_features_description()
    with tab4:
        st.write("#### Track Features Distribution")
        feature = st.selectbox('Select feature:', ['tempo', 'energy', 'valence', 'danceability',  'acousticness', 'instrumentalness', 'album release date'])
        if feature!='album release date':
            # feauture distribution
            fig = px.histogram(filtered_data, x=feature)
            st.plotly_chart(fig)
        else:
            # Bar chart of tracks by release date
            tracks_by_release_date = (filtered_data
             .groupby('album_release_date')
             .agg({'track_id': 'count'})
            )

            fig = go.Figure(data=[
                go.Bar(
                    x=tracks_by_release_date.index, 
                    y=tracks_by_release_date['track_id'], 
                    text=tracks_by_release_date['track_id'],
                )
            ])

            fig.update_layout(
                yaxis_title='Tracks',
                yaxis_showticklabels=True,
                xaxis_title='Album Release Date'
            )
            st.plotly_chart(fig)

            
            
    with tab5:
        tab51, tab52 = st.tabs(['Absolute Counts', 'Relative Counts'])
        with tab51:
            # Bar chart of artist names in descending order
            track_count = filtered_data['artist_name'].value_counts().sort_values(ascending=False)
            fig = px.bar(x=track_count.index, y=track_count.values, text=track_count.values)
            fig.update_layout(
                xaxis_title='Artist',
                yaxis_title='Tracks',
                title=f"Track Counts by Artist for the Top {n} Most Popular Tracks",
                yaxis=dict(
            showticklabels=True  # Hide the y-axis tick labels
            )
            )
            fig.update_traces(textposition='outside') # display the text labels outside the bars

            st.plotly_chart(fig)
    
        with tab52:
            # Bar chart of artist names in descending order
            # total tracks per artist
            total_tracks_per_artist = (data['artist_name']
                                        .value_counts()
                                        .reset_index()
                                        .rename(columns={'count': 'total_tracks'})
            )
            # total tracks per artist for the selected tracks
            selected_tracks_per_artist = (filtered_data['artist_name']
                                            .value_counts()
                                            .reset_index()
            )
            # merge the two dataframes to get the relative count
            relative_tracks_count = pd.merge(selected_tracks_per_artist, total_tracks_per_artist, on='artist_name')
            relative_tracks_count['relative_count'] = (relative_tracks_count['count'] / relative_tracks_count['total_tracks']) * 100
            relative_tracks_count['relative_count_text'] = relative_tracks_count['relative_count'].apply(lambda x: f'{x:.2f}%') 
            relative_tracks_count = relative_tracks_count.sort_values(by='relative_count', ascending=False)
            # bar plot
            fig = px.bar(x=relative_tracks_count['artist_name'], y=relative_tracks_count['relative_count'], text=relative_tracks_count['relative_count_text'])
            fig.update_layout(
                xaxis_title='Artist',
                yaxis_title=f'% of Total Tracks',
                title=f"Percentage of Artist's Total Tracks in Top {n} Most Popular Tracks",
                yaxis=dict(
            showticklabels=True  # Hide the y-axis tick labels
            )
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig)
    
main()
