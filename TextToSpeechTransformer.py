#!pip install edge-tts
#!pip install asyncio

import edge_tts
import nest_asyncio
import asyncio
import os
from typing import List

class TextToSpeechTransformer:
    def __init__(self, voice="en-US-AriaNeural", rate="+0%", pitch="+0Hz"):
        """
        Initializes the text-to-speech transformer with default or custom voice, rate, and pitch.
        Also applies the nest_asyncio fix to avoid conflicts with existing event loops.
        
        :param voice: The voice to use (e.g., 'en-US-AriaNeural').
        :param rate: The speech rate (e.g., '+0%', '-10%', etc.).
        :param pitch: The speech pitch (e.g., '+0Hz', '+5Hz', etc.).
        """
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        # Apply the fix for Colab's already running event loop
        nest_asyncio.apply()
        # Create voiceovers directory if it doesn't exist
        os.makedirs("voiceovers", exist_ok=True)

    async def _generate_voiceover_edge_tts(self, script, output_audio_path):
        """
        Asynchronous method that uses Edge TTS to generate and save voiceover audio.
        
        :param script: The text script to be read.
        :param output_audio_path: Where the generated audio file will be saved.
        """
        # Ensure the script is not empty
        if not script.strip():
            raise ValueError("The script text cannot be empty!")

        communicate = edge_tts.Communicate(
            text=script,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        await communicate.save(output_audio_path)
        print(f"Voiceover saved to: {output_audio_path}")

    def generate_voiceover(self, script: str, output_audio_path: str) -> str:
        """
        Public method to generate a voiceover. Internally calls the asynchronous method.
        
        :param script: The text script to be read.
        :param output_audio_path: Where the generated audio file will be saved.
        :return: Path to the generated audio file
        """
        output_path = os.path.join("voiceovers", output_audio_path)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._generate_voiceover_edge_tts(script, output_path))
        return output_path

    async def _generate_multiple_voiceovers(self, scripts: List[str], base_output_path: str) -> List[str]:
        """
        Asynchronous method to generate multiple voiceovers from a list of scripts.
        
        :param scripts: List of text scripts to be converted to speech
        :param base_output_path: Base path for output audio files
        :return: List of paths to generated audio files in same order as input scripts
        """
        output_paths = []
        tasks = []
        
        for i, script in enumerate(scripts):
            output_path = os.path.join("voiceovers", f"{base_output_path}_{i}.wav")
            output_paths.append(output_path)
            task = self._generate_voiceover_edge_tts(script, output_path)
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        return output_paths

    def generate_multiple_voiceovers(self, sentences: List[str], base_output_path: str = "audio") -> List[str]:
        """
        Public method to generate multiple voiceovers from a list of sentences.
        
        :param sentences: List of sentences to convert to speech
        :param base_output_path: Base name for the output audio files
        :return: List of paths to generated audio files in same order as input sentences
        :raises ValueError: If the sentences list is empty
        """
        if not sentences:
            raise ValueError("The list of sentences cannot be empty")
            
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._generate_multiple_voiceovers(sentences, base_output_path))


# Example usage
if __name__ == "__main__":
    # Sample sentences for demonstration
    test_sentences = [
        "This is a test sentence for demonstration.",
        "We can pass any list of sentences to this generator.",
        "Each sentence will be converted to speech in parallel."
    ]
    
    # Create transformer and process sentences
    transformer = TextToSpeechTransformer()
    output_paths = transformer.generate_multiple_voiceovers(test_sentences)
    print(f"Generated audio files: {output_paths}")
