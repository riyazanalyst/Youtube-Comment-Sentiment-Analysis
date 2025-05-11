import streamlit as st
import os
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import (
    save_video_comments_to_csv, get_channel_info, youtube,
    get_channel_id, get_video_stats
)

# Function to clean old CSVs
def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

# Page config
st.set_page_config(
    page_title='YouTube Comment Analyzer',
    page_icon='📊',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Hide Streamlit branding
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar input
st.sidebar.title("🎥 YouTube Sentiment Analysis")
st.sidebar.markdown("Analyze the **sentiment of comments** on any YouTube video.")
st.sidebar.markdown("---")
youtube_link = st.sidebar.text_input("📌 Paste YouTube Video URL")

# Welcome screen if no link provided
if not youtube_link:
    st.title("📊 YouTube Comment Sentiment Analysis")
    st.markdown(
        """
        Welcome to the **YouTube Comment Analyzer**!  
        Paste a video link in the sidebar to get started.

        🔍 This tool scrapes comments from the video,  
        analyzes their sentiment (positive, negative, neutral),  
        and visualizes the results for you!

        ---
        """
    )
    with st.expander("ℹ️ About this Project"):
        st.write("""
        This project uses **Python**, **Streamlit**, and **NLP (Natural Language Processing)**  
        to analyze public opinion on YouTube videos. It includes:
        
        - Real-time comment scraping
        - Sentiment classification using NLP
        - Visual analytics with bar charts and line graphs
        - Channel and video metadata display

        Developed by ❤️ for data enthusiasts and content creators.
        """)
    
    st.stop()

# Main processing
video_id = extract_video_id(youtube_link)
channel_id = get_channel_id(video_id)

if video_id:
    st.sidebar.success("Video ID: " + video_id)
    csv_file = save_video_comments_to_csv(video_id)
    delete_non_matching_csv_files(os.getcwd(), video_id)
    st.sidebar.success("✅ Comments Scraped & Saved")
    st.sidebar.download_button("📥 Download Comments CSV", data=open(csv_file, 'rb').read(),
                               file_name=os.path.basename(csv_file), mime="text/csv")

    # Channel info
    channel_info = get_channel_info(youtube, channel_id)
    st.title(f"📺 {channel_info['channel_title']}")

    # Channel top section
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(channel_info['channel_logo_url'], width=150)
    with col2:
        st.markdown(f"**Channel Created:** {channel_info['channel_created_date'][:10]}")
        st.markdown(f"**Total Videos:** {channel_info['video_count']}")
        st.markdown(f"**Subscribers:** {channel_info['subscriber_count']}")

    st.markdown("---")

    # Video stats
    stats = get_video_stats(video_id)
    st.subheader("🎬 Video Stats")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Views", stats["viewCount"])
    with col4:
        st.metric("Likes", stats["likeCount"])
    with col5:
        st.metric("Comments", stats["commentCount"])

    st.video(youtube_link)

    # Sentiment Analysis
    st.markdown("---")
    st.subheader("🧠 Sentiment Analysis")
    results = analyze_sentiment(csv_file)
    col6, col7, col8 = st.columns(3)
    with col6:
        st.metric("Positive", results['num_positive'])
    with col7:
        st.metric("Negative", results['num_negative'])
    with col8:
        st.metric("Neutral", results['num_neutral'])

    bar_chart(csv_file)
    plot_sentiment(csv_file)

    # Channel Description
    st.markdown("---")
    st.subheader("📝 Channel Description")
    st.write(channel_info['channel_description'])

else:
    st.error("❌ Invalid YouTube link. Please try again.")
