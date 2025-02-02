import streamlit as st
import appworkflow

def main():
    st.title("Reelwise")

    # User inputs a YouTube link
    video_url = st.text_input("Enter the YouTube video URL:")

    # Trigger Reel creation
    if st.button("Reelize"):
        if not video_url:
            st.error("Please provide a valid YouTube URL.")
        else:
            try:
                engine = appworkflow.Engine(video_url)
                engine.process_video()
                st.success(f"Video was processed successfully!")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
