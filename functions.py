import pandas as pd
import streamlit as st


# for tracks page

def show_tracks_table(filtered_data):
    """Show the table of the most popular tracks.
    Args:
        filtered_data (pandas.DaraFrame): The data to display.
        n (int): The number of rows to display sorted by current popularity.
   """
    df = (filtered_data.sort_values(by='current_track_popularity', ascending=False)
          .reset_index(drop=True)
          .rename_axis('index')
          .reset_index()
          .assign(index=lambda x: x['index'] + 1)
        #.set_index('index')
        )
    
    data_table = st.data_editor(
        df,
        column_order=("chart", "index", "original_track_name", "artist_name", "album_image_medium", "current_track_popularity", "track_id"
                      "track_popularity_list","track_spotify_url", "album_release_date"),
        column_config={
            "chart": "Chart",
            "index": "Rank",
            "original_track_name": "Track",
            "artist_name": "Artist",
           "current_track_popularity": "Popularity",
            "track_spotify_url": st.column_config.LinkColumn("Listen on Spotify"),
            "album_release_date": None,
            "track_id": None,
            "album_image_medium": st.column_config.ImageColumn("Album Artwork", width='small'),
            "track_popularity_list": st.column_config.LineChartColumn(
                "Popularity Trend", y_min=0, y_max=100, width='medium'
            ),
        },
        hide_index=True,
        disabled=("index", "original_track_name", "artist_name", "album_image_medium", "current_track_popularity", "track_popularity_list", "track_spotify_url"),
        use_container_width=False,
        width=3000,
    )
    return data_table
    


# scatter plot with streamlit
def track_features_scatter_plot(filtered_data):
    st.scatter_chart(data=filtered_data, x='valence', y='energy', 
                    size='current_track_popularity', color='mode',)
        

def write_features_description():
# description of the track features
    st.write('''#### Track Features Description''') 
    st.write('''
            `Popularity`: 
                The popularity of a track is a value between 0 and 100, with 100 being the most popular. 
                The popularity is calculated by algorithm and is based, in the most part, on the total
                number of plays the track has had and how recent those plays are.  
                *Note: the popularity value may lag actual popularity by a few days: the value is not updated in real time.*
                ''')
    #st.write('''
    #        `Mode`:
    #            Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived.
    #            ''')
    st.write('''
            `Tempo`:
                The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece
                and derives directly from the average beat duration.
                ''')
    st.write('''
            `Energy`:
                Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. 
                Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy,
                while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range,
                perceived loudness, timbre, onset rate, and general entropy.
                ''')
    st.write('''
            `Valence`:
                A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
                Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric),
                while tracks with low valence sound more negative (e.g. sad, depressed, angry).
                ''')
    st.write('''
            `Danceability`:
                    Danceability describes how suitable a track is for dancing based on a combination of musical elements
                    including tempo, rhythm stability, beat strength, and overall regularity.
                    A value of 0.0 is least danceable and 1.0 is most danceable.
                ''')
    st.write('''
            `Acousticness`:
                A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence
                the track is acoustic.
                ''')
    st.write('''
            `Instrumentalness`:
                Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context.
                Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood
                the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is 
                higher as the value approaches 1.0.
                ''')
    st.write('''Source: [Spotify API](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)''')
    
    

# for artists page
def show_artists_table(filtered_data):
    """Show the table of the most popular tracks.
    Args:
        filtered_data (pandas.DaraFrame): The data to display.
        n (int): The number of rows to display sorted by current popularity.
   """
    df = (filtered_data.sort_values(by='current_artist_popularity', ascending=False)
          .reset_index(drop=True)
          .rename_axis('index')
          .reset_index()
          .assign(index=lambda x: x['index'] + 1)
        #.set_index('index')
        )
    
    data_table = st.data_editor(
        df,
        column_order=("chart", "index", "artist_name", "artist_image_medium", "current_artist_popularity", "artist_popularity_list", "artist_url"),
        column_config={
            "chart": "Chart",
            "index": "Rank",
            "artist_name": "Artist",
           "current_artist_popularity": "Popularity",
            "artist_url": st.column_config.LinkColumn("On Spotify"),
            "artist_image_medium": st.column_config.ImageColumn("Artist Artwork", width='small'),
            "artist_popularity_list": st.column_config.LineChartColumn(
                "Popularity Trend", y_min=0, y_max=100, width='medium'
            ),
        },
        hide_index=True,
        disabled=("index", "artist_name","artist_image_medium", "current_artist_popularity", "artist_popularity_list"),
        use_container_width=False,
        width=3000,
    )
    return data_table

    
# for Clustering page
