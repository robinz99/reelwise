import sys
import subprocess
import os

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

import whisper
import yt_dlp
import re

def download_youtube_transcript(video_url, output_path="downloads"):
    """
    Tries to download a YouTube transcript (official or auto-generated) using yt-dlp.
    If successful, converts it to a .txt file and returns its path.
    """
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # We'll download subtitles (including auto) without the video
        # Then parse them into plain text.
        ydl_opts = {
            'writesubtitles': True,       # Attempt to write subtitles
            'writeautomaticsub': True,    # Include auto-generated subtitles if official ones aren't available
            'subtitleslangs': ['en'],     # Subtitles language
            'subtitlesformat': 'vtt',     # We'll parse .vtt
            'skip_download': True,        # Skip the actual video download
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Setting download=True actually writes the subtitles to disk, 
            # even though skip_download is True for the video.
            info = ydl.extract_info(video_url, download=True)

            base_filename = ydl.prepare_filename(info)
            directory = os.path.dirname(base_filename) or output_path

            # Check for .en.vtt in the directory
            found_subtitles = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if f.endswith('.en.vtt')
            ]
            if not found_subtitles:
                # No .en.vtt => no official or auto subtitles in English
                return None

            vtt_path = found_subtitles[0]
            stem, _ = os.path.splitext(vtt_path)
            transcript_file = stem + '_transcript.txt'

            # Parse VTT -> text, removing <...> tags and skipping lines 
            # that look like metadata or timestamps
            with open(vtt_path, 'r', encoding='utf-8') as fin, open(transcript_file, 'w', encoding='utf-8') as fout:
                for line in fin:
                    line_stripped = line.strip()
                    # Skip lines with 'WEBVTT', numeric counters, timestamps, or known metadata
                    if (line_stripped.startswith('WEBVTT') or
                        line_stripped.isdigit() or
                        '-->' in line_stripped or
                        not line_stripped or
                        line_stripped.startswith('Kind:') or
                        line_stripped.startswith('Language:')):
                        continue

                    # Remove inline tags like <00:00:00.160> or <c> using regex
                    line_stripped = re.sub(r'<[^>]*>', '', line_stripped).strip()

                    # If there's still text left, write it
                    if line_stripped:
                        fout.write(line_stripped + '\n')

            print(f"Transcript downloaded and saved to: {transcript_file}")
            return transcript_file

    except Exception as e:
        print(f"Error while downloading transcript: {e}")
        return None





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
    Attempts to download the YouTube transcript (official or auto-generated). If found,
    saves it in plain text and returns its path. Otherwise, downloads video + audio
    and transcribes the audio with Whisper.
    """
    transcript_file = download_youtube_transcript(video_url, output_path)
    if transcript_file:
        # We got a transcript file, so return it.
        return transcript_file

    # If no transcript found, do the manual approach.
    video_file, audio_file = download_youtube_video_and_audio(video_url, output_path)
    # Transcribe the audio
    transcription = transcribe_audio(audio_file)

    # Save transcription to a text file (same name as audio file, plus suffix)
    transcription_file = os.path.splitext(audio_file)[0] + "_transcription.txt"
    with open(transcription_file, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"Transcription saved to: {transcription_file}")

    return transcription_file
