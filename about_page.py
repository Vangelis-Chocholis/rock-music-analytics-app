import streamlit as st

st.title('📜 About this app')

st.subheader('🎯 Goal')
st.write('''
         The goal of this app is to visualize data for legendary rock artists and make it easy for users to explore and answer questions
         through interactive data visualizations.
         
         For users who are not familiar with rock music, this app offers an opportunity to discover popular tracks that are a good starting point to explore Rock music.
         The Rock music fans can also be benefited from this app by exploring unpopular tracks of their favorite artists that are amazing but not well-known, 
         or discover tracks by using the audio features filters.
         
         Last but not least, this app provides a clustering analysis of tracks based on their audio features. Users can answer questions like 
         "Which cluster do the most popular tracks belong to?" or "How many tracks from your favorite artist are found in each cluster?" 
        
         ''')
st.subheader('🗃️ Data')
st.write('''
        The data have been collected from the Spotify API and stored in a cloud database. An automated E.T.L. process is running every day to update the data.
        For details about the E.T.L. process, please refer to the github repository link below.
        
        **Disclaimer**: The 30 legendary rock artists were selected based on my personal experience with Rock music and may not represent the general opinion.
        Artists from genres such as Metal, Punk Rock, and others are not included, even though they are also considered legendary
        (i.e Metallica, Black Sabbath, Ramones and many more).
         ''')

st.subheader('🔗 Links')
st.write('''
         📌 [Streamlit App GitHub repository](https://github.com/Vangelis-Chocholis/rock-music-analytics-app)
         
         📌 [E.T.L. GitHub repository](https://github.com/Vangelis-Chocholis/ETL_Spotify_data)
         ''')
