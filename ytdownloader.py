import sys
import subprocess
import os
import whisper

# Install required packages
def install_package(package_name):
    """Helper function to install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"'{package_name}' has been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing '{package_name}': {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Install required packages
install_package("yt-dlp")
install_package("openai-whisper") 
install_package("streamlit")

def download_youtube_audio(video_url, output_path="downloads"):
    """
    Downloads a YouTube audio as mp3 file using yt-dlp.
    
    Parameters:
    - video_url (str): The URL of the YouTube video.
    - output_path (str): The directory where the audio will be saved.
    
    Returns:
    - String: Path to the downloaded audio file.
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Download the audio file (MP3)
        audio_output_template = os.path.join(output_path, "%(title)s.mp3")
        audio_command = [
            "yt-dlp",
            video_url,
            "-o", audio_output_template,
            "--extract-audio",
            "--audio-format", "mp3"
        ]
        print("Downloading audio...")
        subprocess.run(audio_command, check=True)

        # Locate the downloaded files
        downloaded_file = os.listdir(output_path)

        audio_file = next(
            (os.path.join(output_path, f) for f in downloaded_file
             if f.endswith(".mp3")),
            None
        )

        if not audio_file:
            raise Exception("Failed to download audio file.")

        print(f"Downloaded audio file: {audio_file}")
        return audio_file

    except subprocess.CalledProcessError as e:
        print(f"Error occurred during download: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def transcribe_audio(file_path):
    """
    Transcribes an audio file using OpenAI's Whisper model.
    
    Parameters:
    - file_path (str): Path to the audio file.
    
    Returns:
    - str: The transcription text.
    """
    try:
        print(f"File to be transcribed: {file_path}")
        
        # Ensure file exists
        if not os.path.exists(file_path):
            raise Exception(f"Audio file does not exist: {file_path}")
            
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        
        print("Transcribing audio...")
        result = model.transcribe(file_path)
        transcription = result["text"]
        
        print("Transcription completed.")
        return transcription
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise

def process_youtube_link(video_url, output_path="downloads"):
    """
    Orchestrates the download of audio and transcribes the audio.
    Returns the path to the saved transcription file.
    """
    # Download both video and audio
    audio_file = download_youtube_audio(video_url, output_path)
    
    # Transcribe the audio
    transcription = transcribe_audio(audio_file)
    
    # Save transcription to a text file (same name as audio file, plus suffix)
    transcription_file = os.path.splitext(audio_file)[0] + "_transcription.txt"
    with open(transcription_file, "w", encoding="utf-8") as f:
        f.write(transcription)
        
    print(f"Transcription saved to: {transcription_file}")
    return transcription_file
