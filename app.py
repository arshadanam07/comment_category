import streamlit as st
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

# Set up your Google API key in the environment variables
# You need to enable the YouTube Data API v3 in your Google Cloud Console
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

prompt = """You are Youtube video comments categorizer./ You will be taking all the comments from that video and analyze the all the comments./
From the analysis of the comments you will categorize the comments as Time stamp comments if the comment has time stamp in it. For Example ""Wow really loved the 1:15 part"
or " Wow 2:25 was facinating/
Similarly those comments which are directly indicating that they liked or disliked the video but not specifying what they liked or disliked comes under the category of basic comments. 
For example "Really loved the vide"or "Didn't like the video at all"./There may be comments where the subscriber mentioned explicitly
what they liked about the video, they could mention person or an object or a specific topic that they liked about the video. Those comments
comes under the category of content based comment. For example  "I really loved the american war video" or "I loved the friendship between you three friends" or "I laughed a lot at 
the entry of the little girl"./ Similarly there may be comments where the subsciber mentioned about what they like about the content creator it could be the style, research or 
any other thing. So these comments comes under the category of creator based comment. For example "hey loved your editing style", "I always appreciate the way you rearch".
If the  subscriber directly mentioned that make videos on this topic so those comments will come under the category of topic based comments. For example " Make video on iran-irag war",
"Make videos on alia bhatt" or "Make a playlist on deep learning" or "What about Machine learning playlist.
/The main difference between creator based comments and content based comment is that subscriber if mentioned what they like about the content creator
then it is a creator based comments and if the subscriber mentioned about what they like in the video then it is content based comment. 

 Finally print all the comments in their specific categories in this format
 1. Topic based comments
 2. Content based comments
 3. Creator based comments
 4. Basic comments
 5. Time stamp comments
 6. Uncategorized comments"""

def get_video_comments(video_id):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    )
    while request:
        response = request.execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        request = youtube.commentThreads().list_next(request, response)
    return comments

def get_video_id(youtube_link):
    if "youtube.com" in youtube_link:
        video_id = youtube_link.split("v=")[1].split("&")[0]
    elif "youtu.be" in youtube_link:
        video_id = youtube_link.split("/")[-1].split("?")[0]
    else:
        video_id = None
    return video_id

def categorize_comments(comments, categories):
    categorized_comments = {category: [] for category in categories}
    categorized_comments['Uncategorized'] = []  # Initialize Uncategorized category
    model = genai.GenerativeModel("gemini-pro")

    for comment in comments:
        response = model.generate_content(prompt + comment)
        category_found = False
        for category in categories:
            if category.lower() in response.text.lower():
                categorized_comments[category].append(comment)
                category_found = True
                break
        if not category_found:
            categorized_comments['Uncategorized'].append(comment)

    return categorized_comments

st.title("Youtube Video Comments Categorizer")
youtube_link = st.text_input("Enter Youtube Video Link:")

if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Categorize Comments"):
    if video_id:
        comments = get_video_comments(video_id)

        if comments:
            categories = ["Content based","Creator based","Topic based","Time stamp","Basic"]  # Example categories
            categorized_comments = categorize_comments(comments, categories)

            st.markdown("## Categorized Comments:")
            for category, comments_list in categorized_comments.items():
                st.markdown(f"### {category.capitalize()}:")
                for comment in comments_list:
                    st.write(comment)
        else:
            st.write("No comments found for this video.")
    else:
        st.write("Please enter a valid YouTube video link.")
