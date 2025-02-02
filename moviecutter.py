#pip install moviepy==1.0.3
#pip install --upgrade imageio decorator
#pip install moviepy==2.0.0
import os
from moviepy.editor import ImageSequenceClip, ImageClip, AudioFileClip, concatenate_videoclips

class MovieCutter:
    def __init__(self, script_sentences, audio_paths, image_paths):
        if not (len(script_sentences) == len(audio_paths) == len(image_paths)):
            raise ValueError("Number of sentences, audio files, and images must match")
        
        # Validate all files exist
        for audio_path in audio_paths:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        for image_path in image_paths:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
        self.pairs = list(zip(script_sentences, audio_paths, image_paths))
        self.clips = []

    def create_clip(self, image_path, audio_path):
        """Create a video clip from an image and audio file."""
        try:
            audio_clip = AudioFileClip(audio_path)
            clip = ImageClip(image_path).set_duration(audio_clip.duration)
            return clip.set_audio(audio_clip)
        except Exception as e:
            raise RuntimeError(f"Failed to create clip from {image_path} and {audio_path}: {str(e)}")

    def generate_clips(self):
        """Generate video clips for each sentence-audio-image pair."""
        self.clips = []  # Reset clips list
        for sentence, audio_path, image_path in self.pairs:
            try:
                clip = self.create_clip(image_path, audio_path)
                self.clips.append(clip)
            except Exception as e:
                raise RuntimeError(f"Failed to generate clip: {str(e)}")
        return self

    def concatenate_clips(self):
        """Combine all clips into a single video."""
        if not self.clips:
            raise ValueError("No clips to concatenate. Call generate_clips() first.")
        return concatenate_videoclips(self.clips, method="compose")

    def create_video(self, output_filename="final_educational_reel.mp4", fps=24):
        """Create the final video file."""
        if not self.clips:
            self.generate_clips()
        
        # Validate output directory exists
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        try:
            final_video = self.concatenate_clips()
            final_video.write_videofile(output_filename, fps=fps)
            return output_filename
        except Exception as e:
            raise RuntimeError(f"Failed to create video: {str(e)}")
