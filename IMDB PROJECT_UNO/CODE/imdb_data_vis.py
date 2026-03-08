import streamlit as sl
import pandas as pd
import mysql.connector
import matplotlib.pyplot as pyt
import plotly.express as px
import seaborn as sea
connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Roronoa7*",
    database = "IMDB_Dataset"
)

query = "with RankedMovieData as (select movie_name, rationgs, genre, user_vote_count, duration, ROW_NUMBER() OVER (PARTITION BY movie_name ORDER BY rationgs desc, user_vote_count desc) as rn FROM imdb_movie_data WHERE user_vote_count > 50000) select movie_name, genre, duration, rationgs, user_vote_count from RankedMovieData where rn = 1 order by rationgs desc, user_vote_count desc LIMIT 10"

sl.subheader("🎬 1. Top 10 Movies by Rating and Voting Counts")

sql_df = pd.read_sql(query, connection)

sl.dataframe(
     sql_df,
     column_config={
         "movie_name": "Movie Name",
         "genre": "Movie Genre",
         "duration": "Duration",
         "rationgs": sl.column_config.NumberColumn(
             "Movie Ratings",
             help="Number of stars on IMDB",
             format="%f ⭐",
         ),
         "user_vote_count": "User Votes",
     },
     hide_index=True,
 )

sl.subheader("🎬 2. Genre Distribution")

bar_query = "select count(movie_name) as Movie_Count, genre as Genre from imdb_movie_data group by genre"
bar_chart_df = pd.read_sql(bar_query, connection)
sl.bar_chart(bar_chart_df, x="Genre", y="Movie_Count", color='#FF0000')

sl.subheader("🕰️ 3. Average Duration by Genre")

hor_bar_query = "select avg(duration) as Average_Duration, genre as Genre from imdb_movie_data group by genre"
hor_bar_chart_df = pd.read_sql(hor_bar_query, connection)
sl.bar_chart(hor_bar_chart_df, x="Genre", y="Average_Duration", color='#0000FF', horizontal=True)

sl.subheader("👤 4. Voting Trends by Genre")

avg_vote_query = "select avg(user_vote_count) as Average_Voting_Count, genre as Genre from imdb_movie_data group by genre"
avg_bar_chart_df = pd.read_sql(avg_vote_query, connection)
sl.bar_chart(avg_bar_chart_df, x="Genre", y="Average_Voting_Count", color='#00FF00', horizontal=True)

sl.subheader("⭐️ 5. Rating Distribution")

hist_query = "select rationgs from imdb_movie_data"
hist_df = pd.read_sql(hist_query, connection)
hist_list = hist_df['rationgs']
fig, ax = pyt.subplots()
ax.hist(hist_list, bins=10)

sl.pyplot(fig)

sl.subheader("⭐️ 6. Genre-Based Rating Leaders")

genre_rating_query = "select movie_name as Movie_Name, rationgs as Ratings, genre as Genre from imdb_movie_data"
genre_rating_df = pd.read_sql(genre_rating_query, connection)
max_ratings = genre_rating_df.groupby('Genre')['Ratings'].transform('max')
highlight_df = genre_rating_df.style.applymap(
    lambda val: 'background-color: #ffe599' if val in max_ratings.values else '', subset='Ratings'
)
sl.dataframe(highlight_df, use_container_width=True)


sl.subheader("🎥 7. Most Popular Genres by Voting")

pie_query = "select sum(user_vote_count) as User_Count, genre as Genre from imdb_movie_data group by genre"
pie_chart_df = pd.read_sql(pie_query, connection)
pie_fig = px.pie(pie_chart_df, values='User_Count', names= 'Genre')
sl.plotly_chart(pie_fig, use_container_width=True)

sl.subheader("🕰️ 8. Duration Extremes")

durartion_extremes_query = "select movie_name as Movie, duration as Duration from imdb_movie_data"
durartion_extremes_df = pd.read_sql(durartion_extremes_query, connection)
durartion_extremes_df = durartion_extremes_df[durartion_extremes_df['Duration']>0]
shortest_movie = durartion_extremes_df[durartion_extremes_df['Duration'] == durartion_extremes_df['Duration'].min()]
longest_movie = durartion_extremes_df[durartion_extremes_df['Duration'] == durartion_extremes_df['Duration'].max()]
shortest_movie['Type'] = 'Shortest Movie'
longest_movie['Type'] = 'Longest Movie'
short_long_movie = pd.concat([shortest_movie,longest_movie], ignore_index= True)
sl.dataframe(short_long_movie, hide_index= True, use_container_width= True)


sl.subheader("⭐️ 9. Ratings by Genre")

avg_ratings_query = "select genre as Genre, avg(rationgs) as Average_Ratings from imdb_movie_data group by genre"
avg_ratings_df = pd.read_sql(avg_ratings_query, connection)
pyt.figure(figsize=(6,5))
sea.heatmap(avg_ratings_df.pivot_table(index='Genre', values='Average_Ratings'), annot=True, cmap='YlGnBu', fmt =".1f", linewidths=0, cbar=True)
sl.pyplot(pyt)

sl.subheader("🎥 10. Correlation Analysis")

scatter_query = "select rationgs as Ratings, user_vote_count as Voting_Counts from imdb_movie_data"
scatter_df = pd.read_sql(scatter_query, connection)
sl.scatter_chart(scatter_df, x= "Ratings", y = "Voting_Counts", color="#FFEECC")

sl.subheader("Interactive Filtering Functionality")

duration_option = sl.multiselect('Select Duration', ["< 2 hrs", "2-3 hrs", "> 3 hrs"])
def duration_filter(df):
    if not duration_option:
        return pd.Series([True] * len(df))
    duration_selection = pd.Series([False] * len(df))
    for option in duration_option:
        if option == "< 2 hrs":
            duration_selection |= df['duration'] < 120
        elif option == "2-3 hrs":
            duration_selection |= (df['duration'] >= 120) & (df['duration'] <= 180)
        elif option == ">3 hrs":
            duration_selection |= df['duration'] > 180   
    return duration_selection

rating_option = sl.multiselect('Select Rating', ["<5.0", ">5.0", ">6.0", ">7.0", ">8.0", ">9.0"])
def rating_filter(df):
    if not rating_option:
        return pd.Series([True] * len(df))
    rating_selection =pd.Series([False] * len(df))
    for option in rating_option:
        if option == "<5.0":
            rating_selection |= df['rationgs'] < 5.0
        elif option == ">5.0":
            rating_selection |= df['rationgs'] > 5.0
        elif option == ">6.0":
            rating_selection |= df['rationgs'] > 6.0
        elif option == ">7.0":
            rating_selection |= df['rationgs'] > 7.0
        elif option == ">8.0":
            rating_selection |= df['rationgs'] > 8.0
        elif option == ">9.0":
            rating_selection |= df['rationgs'] > 9.0
    return rating_selection

user_count_option = sl.multiselect('Select User Count', ["<10000", ">10000", ">25000", ">50000", ">100000"])
def user_count_filter(df):
    if not user_count_option:
        return pd.Series([True] * len(df))
    user_count_selection = pd.Series([False] * len(df))
    for option in user_count_option:
        if option == "<10000":
            user_count_selection |= df['user_vote_count'] < 10000
        elif option == ">10000":
            user_count_selection |= df['user_vote_count'] > 10000
        elif option == ">25000":
            user_count_selection |= df['user_vote_count'] > 25000
        elif option == ">50000":
            user_count_selection |= df['user_vote_count'] > 50000
        elif option == ">100000":
            user_count_selection |= df['user_vote_count'] > 100000
    return user_count_selection

filtered_query = "select * from imdb_movie_data"
filtered_df = pd.read_sql(filtered_query, connection)
genre_option = sl.multiselect('Select Genre', options=list(filtered_df['genre'].unique())) 
genre_choice = filtered_df['genre'].isin(genre_option) if genre_option else pd.Series([True] * len(filtered_df))
duration_choice= duration_filter(filtered_df)
rating_choice = rating_filter(filtered_df)
user_count_choice = user_count_filter(filtered_df)
if not genre_option and not duration_option and not rating_option and not user_count_option:
    sl.dataframe(filtered_df, column_config={
         "movie_name": "Movie Name",
         "genre": "Movie Genre",
         "duration": "Duration",
         "rationgs": sl.column_config.NumberColumn(
             "Movie Ratings",
             help="Number of stars on IMDB",
             format="%f ⭐",
         ),
         "user_vote_count": "User Votes",
     },hide_index=True, use_container_width=True)
else:
    filtered_movies = filtered_df[genre_choice & duration_choice & rating_choice & user_count_choice]
    sl.dataframe(filtered_movies,column_config={
         "movie_name": "Movie Name",
         "genre": "Movie Genre",
         "duration": "Duration",
         "rationgs": sl.column_config.NumberColumn(
             "Movie Ratings",
             help="Number of stars on IMDB",
             format="%f ⭐",
         ),
         "user_vote_count": "User Votes",
     }, hide_index=True, use_container_width=True)