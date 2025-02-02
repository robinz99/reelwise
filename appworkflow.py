from llamarizer import LLaMarizer
from imagescraper import ImageScraper
from ytdownloader import process_youtube_link
from TextToSpeechTransformer import TextToSpeechTransformer
from moviecutter import MovieCutter

class Engine:
    def __init__(self, video_url: str, output_path: str = "downloads"):
        self.video_url = video_url
        self.output_path = output_path
        self.llamarizer = LLaMarizer(use_cuda=False)
        self.scraper = ImageScraper(save_folder="images")
        self.transformer = TextToSpeechTransformer()
        self.transcription_file = None
        self.script_text = None
        self.processed_script = None
        self.bing_terms = None
        self.image_paths = None
        self.voiceover_paths = None

    def process_video(self):
        try:
            # Download and transcribe video
            self.transcription_file = process_youtube_link(self.video_url, self.output_path)
            print(f"Transcription saved to: {self.transcription_file}")
            
            # Read transcription
            with open(self.transcription_file, 'r', encoding='utf-8') as f:
                transcript = f.read()

            # Generate and process script
            script_output = self.llamarizer.generate_script(transcript)
            self.script_text = script_output[0]["generated_text"][-1]["content"]
            print("Valid script generated:", self.script_text)
            
            # Split script into a list of sentences
            self.processed_script = self.llamarizer.process_script(self.script_text)
            print(self.processed_script)

            # Generate search terms and download images
            self.bing_terms = self.llamarizer.generate_multiple_bing_search_terms(self.processed_script)
            print(self.bing_terms)
            
            self.image_paths = self.scraper.download_images_for_bing_prompts(self.bing_terms)
            print(self.image_paths)

            # Create voiceover for script sentences
            self.voiceover_paths = self.transformer.generate_multiple_voiceovers(self.processed_script)
            print(f"Generated audio files: {self.voiceover_paths}")

            #Combine all components into one video
            movie = MovieCutter(self.processed_script, self.voiceover_paths, self.image_paths)
            output_path = movie.create_video()
            print(f"Video created at: {output_path}")

            return True

        except Exception as e:
            print(f"Error processing video: {e}")
            return False