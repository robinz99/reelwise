import sys
import subprocess

#Install library yt-dlp for youtube video download functionality

package_name = "yt-dlp"

try:
    # Use subprocess to run the pip command
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    print(f"'{package_name}' has been successfully installed.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while installing '{package_name}': {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

#Install library openai-whisper for transcribing

package_name = "openai-whisper"

try:
    # Use subprocess to run the pip command
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    print(f"'{package_name}' has been successfully installed.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while installing '{package_name}': {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

#Install library streamlit for application

package_name = "streamlit"

try:
    # Use subprocess to run the pip command
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    print(f"'{package_name}' has been successfully installed.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while installing '{package_name}': {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

import os
import subprocess
import whisper

def download_youtube_video_and_audio(video_url, output_path="downloads"):
    """
    Downloads a YouTube video and its audio as separate files using yt-dlp, without merging them.

    Parameters:
    - video_url (str): The URL of the YouTube video.
    - output_path (str): The directory where the video and audio will be saved.

    Returns:
    - tuple: Paths to the downloaded video file and audio file.
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Download the video file (only video, no merge)
        video_output_template = os.path.join(output_path, "%(title)s.%(ext)s")
        video_command = [
            "yt-dlp",
            video_url,
            "-o", video_output_template,
            "--format", "bestvideo"  # Download only the best video
        ]
        print("Downloading video...")
        subprocess.run(video_command, check=True)

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
        downloaded_files = os.listdir(output_path)
        video_file = next(
            (os.path.join(output_path, f) for f in downloaded_files
             if f.endswith((".mp4", ".mkv", ".webm"))),
            None
        )
        audio_file = next(
            (os.path.join(output_path, f) for f in downloaded_files
             if f.endswith(".mp3")),
            None
        )

        if not video_file or not audio_file:
            raise Exception("Failed to download both video and audio files.")

        print(f"Downloaded video file: {video_file}")
        print(f"Downloaded audio file: {audio_file}")
        return video_file, audio_file

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
    Orchestrates the download of video/audio and transcribes the audio.
    Returns the path to the saved transcription file.
    """
    # Download both video and audio
    video_file, audio_file = download_youtube_video_and_audio(video_url, output_path)

    # Transcribe the audio
    transcription = transcribe_audio(audio_file)

    # Save transcription to a text file (same name as audio file, plus suffix)
    transcription_file = os.path.splitext(audio_file)[0] + "_transcription.txt"
    with open(transcription_file, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"Transcription saved to: {transcription_file}")

    return transcription_file
