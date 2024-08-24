import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
#import plotly.colors
import numpy as np




@st.cache_data
def get_clustered_data(file_path):
    """
    Reads a CSV file, processes the data, and merges it with cached clustering data.

    This function performs the following steps:
    1. Reads the CSV file from the provided file path.
    2. Converts the 'cluster' column to string type.
    3. Creates a new column 'hover_info' by concatenating 'original_track_name' and 'artist_name'.
    4. Checks for 'cached_clustering_data' in the session state and raises a KeyError if not found.
    5. Merges the read data with the cached clustering data on 'track_id'.
    6. Returns the processed DataFrame.

    If any error occurs during these steps, an error message is displayed using Streamlit's error handling, 
    and the function returns None.

    Parameters:
    file_path (str): The file path of the CSV file to be read.

    Returns:
    pd.DataFrame: The processed DataFrame containing the merged data.
    None: If an error occurs during processing.
    """
    try:
        data = pd.read_csv(file_path)
        data = data.astype({'cluster': 'str'})
        data['hover_info'] = data['original_track_name'] + ' by ' + data['artist_name']
        
        if 'cached_clustering_data' not in st.session_state:
            raise KeyError("cached_clustering_data not found in session state")
        
        cached_data = st.session_state['cached_clustering_data']
        data = pd.merge(data, cached_data, on='track_id')
        
        return data
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# mean popularity by cluster
@st.cache_data
def clustered_data_trend():
    """
    Reads track data, merges them, and calculates the mean popularity of tracks
    grouped by date and cluster.

    The function performs the following steps:
    1. Reads 'track_id' and 'track_name' from 'data/tracks_table.csv'.
    2. Reads 'track_id' and 'cluster' from 'data/tracks_clustered.csv'.
    3. Reads all columns from 'data/tracks_popularity_table.csv'.
    4. Merges the data from the three CSV files on 'track_id'.
    5. Groups the merged data by 'date' and 'cluster', and calculates the mean 'track_popularity'.
    6. Returns the grouped data as a DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the mean popularity of tracks grouped by date and cluster.
    """
    # read the data
    tracks_table = pd.read_csv('data/tracks_table.csv')[['track_id', 'track_name']]
    tracks_clustered = pd.read_csv('data/tracks_clustered.csv')[['track_id', 'cluster']]
    tracks_clustered['cluster'] = tracks_clustered['cluster'].astype(str)
    #tracks_popularity = pd.read_csv('data/tracks_popularity_table.csv')
    try:
        if 'cached_tracks_popularity_table' not in st.session_state:
            raise KeyError("cached_tracks_popularity_table not found in session state")
        tracks_popularity = st.session_state['cached_tracks_popularity_table']
    
        tracks_data = pd.merge(tracks_table, tracks_clustered, on='track_id')
        tracks_data = pd.merge(tracks_data, tracks_popularity, on='track_id')
        # group by date and cluster aggregating the mean popularity
        group = (tracks_data
                .groupby(['date', 'cluster'])
                .agg({'track_popularity': 'mean'})
                .reset_index()
        )
        return group
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None          
             
             
def cluster_scatter_plot(df, x, y, z):
    """
    Generate a 3D scatter plot with clustered data.

    Args:
        df (pandas.DataFrame): The input dataframe containing the data.
        x (str): The column name for the x-axis.
        y (str): The column name for the y-axis.
        z (str): The column name for the z-axis.

    Returns:
        plotly.graph_objects.Figure: The generated 3D scatter plot.
    """
    fig = px.scatter_3d(
        data_frame=df,
        x=x,
        y=y,
        z=z,
        opacity=1,
        color='cluster',
        color_discrete_map={'0': '#fde725', '1': '#5ec962', '2': '#21918c',
                            '3': '#3b528b', '4': '#440154'},
        category_orders={'cluster': ['0', '1', '2', '3', '4']},
        hover_name='hover_info',
    )
    # Update marker size
    fig.update_traces(marker=dict(size=4))
    # margins
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig


def cluster_features_heatmap(clustered_data):
    group = (clustered_data
            .groupby('cluster')[['danceability', 'energy', 'loudness_scaled', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo_scaled']]
            .mean()
    )
    # Convert the DataFrame to a 2D numpy array
    data_array = group.to_numpy()

    # Define the custom color scale
    colors = ['white', 'lightblue', 'blue', 'darkblue']
    color_scale = [[0, colors[0]], [0.33, colors[1]], [0.66, colors[2]], [1, colors[3]]]

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=data_array,
        x=group.columns,
        y=group.index,
        colorscale=color_scale,
        zmin=0,
        zmax=1,
        text=np.round(data_array, 2),
        texttemplate="%{text}",
        textfont={"color": "black"}
    ))

    # Add title and axis labels
    fig.update_layout(
        #title='Heatmap of Cluster Means',
        xaxis_title='Features',
        yaxis_title='Clusters',
        xaxis_nticks=len(group.columns),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(group.index))),
            ticktext=group.index
        )
    )
    return fig


def cluster_trend_plot(clustered_data_trend):
    fig = px.line(
        clustered_data_trend,
        x='date',
        y='track_popularity',
        color='cluster',
        color_discrete_map={'0': '#fde725', '1': '#5ec962', '2': '#21918c',
                            '3': '#3b528b', '4': '#440154'},
        category_orders={'cluster': ['0', '1', '2', '3', '4']},
        labels={'track_popularity': 'Mean Track Popularity', 'cluster': 'Cluster'},
        #title='Popularity Trend by Cluster'
    )
    return fig

#########################
# App interface
st.title('📊 Clustering Analysis')
# get the clustered data
clustered_data = get_clustered_data(file_path='data/tracks_clustered.csv')


# sidebar
st.sidebar.title('Filters')
# track popularity slider
selected_track_popularity = st.sidebar.slider('Select a Track Popularity Range', value=[0, 100])
# artist selection

artist_options = ['All Artists'] + clustered_data['artist_name'].unique().tolist()
selected_artist = st.sidebar.selectbox('Select an Artist', artist_options, key='artist_selection_scatter_plot')
    
if selected_artist == 'All Artists':
    filtered_data = clustered_data
else:
    filtered_data = clustered_data.query('artist_name == @selected_artist')

# filter the data based on the selected track popularity range
filtered_data = filtered_data.query('current_track_popularity >= @selected_track_popularity[0] & current_track_popularity <= @selected_track_popularity[1]')


# cluster interpretation
html_content = '''
#### Cluster interpretation
<p><span style="color: #fde725;">Cluster 0:</span> Low <code>valence</code>, High <code>energy</code>, High <code>loudness</code>, High <code>tempo</code>.<br>
This cluster includes energetic and loud tracks that are generally negative in mood (e.g., sad, depressed, angry).</p>

<p><span style="color: #5ec962;">Cluster 1:</span> Low <code>valence</code>, Low <code>energy</code>, High <code>acousticness</code>, High <code>instrumentalness</code> , Lower <code>tempo</code> .<br>
This cluster includes instrumental acoustic tracks with a negative mood, characterized by low energy and a slower tempo.</p>

<p><span style="color: #21918c;">Cluster 2:</span> High <code>valence</code>, High <code>energy</code>, High <code>danceability</code>, High <code>loudness</code>, Higher <code>tempo</code>.<br>
This cluster consists of tracks that are positive in mood (e.g., happy, cheerful, euphoric), energetic, loud, and danceable.</p>

<p><span style="color: #3b528b;">Cluster 3:</span> Medium to Low <code>valence</code>, High <code>energy</code>,  High <code>acousticness</code>, High <code>loudness</code>.<br>
This cluster includes non-instrumental acoustic tracks that have low energy and are generally not highly positive in mood.</p>

<p><span style="color: #440154;">Cluster 4:</span> Relatively High <code>valence</code>, High <code>energy</code>, High <code>instrumentalness</code>, High <code>loudness</code>, Higher <code>tempo</code>.<br>
This cluster consists of instrumental tracks that are positive in mood and highly energetic.</p>
'''

tab1, tab2, tab3, tab4, tab5 = st.tabs(['3D Scatter Plot', 'Features Heatmap', 'Number of Tracks', 'Popularity Trend by Cluster', 'Jupyter Notebooks'])
with tab1:
    # Display the scatter plot
    st.write('#### 3D Scatter Plot of Clusters')
    z = st.selectbox('Select z-axis', ['instrumentalness', 'acousticness' ])
    fig = cluster_scatter_plot(filtered_data, x='energy', y='valence', z=z)
    st.plotly_chart(fig, use_container_width=True)
    # cluster interpretation
    st.markdown(html_content, unsafe_allow_html=True)
    
with tab2:
    st.write('#### Heatmap of Average Feature Values by Cluster')
    st.write('The aggregation has been applied to all tracks in the dataset. Sidebar filters are not applied to this plot.')
    # Show the figure
    fig = cluster_features_heatmap(clustered_data)
    st.plotly_chart(fig, use_container_width=True)
    # cluster interpretation
    st.markdown(html_content, unsafe_allow_html=True)

with tab3:
    # Display the number of tracks per cluster by artist
    group = (filtered_data
            .groupby(['artist_name', 'cluster'])
            .agg({'track_id': 'count'})
            .reset_index()
            .groupby('cluster')
            .agg({'track_id': 'sum'})
            .reset_index()
    )
    # Convert cluster to categorical type to ensure categorical treatment
    group['cluster_display'] = group['cluster'].apply(lambda x: f'Cluster {x}')
    # Create the bar plot
    fig = px.bar(
        group, 
        x='cluster_display', 
        y='track_id',
        labels={'track_id': 'Number of Tracks', 'cluster': 'Cluster'},
        title=f'Number of Tracks per Cluster for {selected_artist}',
        text='track_id',
        category_orders={'cluster_display': ['0', '1', '2', '3', '4']}
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    # cluster interpretation
    st.markdown(html_content, unsafe_allow_html=True)
    
with tab4:
    st.write('#### Mean Popularity Trend by Cluster')
    st.write('''The following plot displays the mean popularity of tracks by cluster and date. 
             The aggregation has been applied to all tracks in the dataset. Sidebar filters are not applied to this plot.''')
    # Get the popularity trend data
    popularity_data = clustered_data_trend()
    # Create the line plot
    fig = cluster_trend_plot(popularity_data)  
    st.plotly_chart(fig, use_container_width=True)
    # cluster interpretation
    st.markdown(html_content, unsafe_allow_html=True)
    
with tab5:
    tab51, tab52 = st.tabs(['Exploratory Data Analysis', 'Clustering'])
    # EDA notebook tab
    with tab51:
        st.write('#### Exploratory Data Analysis')
        path_to_html = "files/EDA.html" 
        with open(path_to_html, 'r', encoding='utf-8') as f:
            html_data = f.read()
        # display the HTML content
        st.components.v1.html(html_data, scrolling=True, height=1000, width=1100)
    # clustering notebook tab
    with tab52:
        st.write('#### Clustering Analysis')
        path_to_html = "files/clustering_notebook.html" 
        with open(path_to_html, 'r', encoding='utf-8') as f:
            html_data = f.read()
        # display the HTML content
        st.components.v1.html(html_data, scrolling=True, height=1000, width=1100)












