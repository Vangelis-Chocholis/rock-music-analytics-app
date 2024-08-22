import  streamlit as st



# --- PAGE SETUP ---
main_page = st.Page(
    "main.py",
    title="Tracks",
    #icon=":material/account_circle:",
    icon="🎸",
    default=True,
)
artists_page = st.Page(
    "artists_page.py",
    title="Artists",
    #icon=":material/bar_chart:",
    icon="🧑🏽‍🎤",
)
clustering_page = st.Page(
    "clustering_page.py",
    title="Clustering",
    #icon=":material/bar_chart:",
    icon="📊",
)
about_page=st.Page(
    "about_page.py",
    title="About",
    #icon=":material/bar_chart:",
    icon="📜",
)
# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
pg = st.navigation(pages=[main_page, artists_page, clustering_page, about_page])
st.session_state.update(st.session_state)
pg.run()

