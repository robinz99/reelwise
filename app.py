import streamlit as st
import os

# Import the functions from your module
from ytdownloader import process_youtube_link

def main():
    st.title("YouTube Downloader & Transcriber")

    # 1. User inputs a YouTube link
    video_url = st.text_input("Enter the YouTube video URL:")

    # 2. User can optionally specify an output folder
    output_path = st.text_input("Enter the output directory (default is 'downloads'):", value="downloads")

    # 3. Trigger download & transcription
    if st.button("Download & Transcribe"):
        if not video_url:
            st.error("Please provide a valid YouTube URL.")
        else:
            try:
                transcription_file = process_youtube_link(video_url, output_path)
                st.success(f"Transcription saved to: {transcription_file}")
                
                # Optionally read and display the transcription
                with open(transcription_file, 'r', encoding='utf-8') as f:
                    st.subheader("Transcription Preview:")
                    st.write(f.read())
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
