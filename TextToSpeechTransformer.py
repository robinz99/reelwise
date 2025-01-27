#!pip install edge-tts
#!pip install asyncio

import edge_tts
import nest_asyncio
import asyncio

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

    def generate_voiceover(self, script, output_audio_path):
        """
        Public method to generate a voiceover. Internally calls the asynchronous method.
        
        :param script: The text script to be read.
        :param output_audio_path: Where the generated audio file will be saved.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._generate_voiceover_edge_tts(script, output_audio_path))


# Example usage
if __name__ == "__main__":
    # Script text and output path for demonstration
    script_text = "This is a sample voiceover generated using Edge TTS."
    output_path = "voiceover_edge.wav"

    # Instantiate the class (optionally specify voice, rate, pitch)
    tts_transformer = TextToSpeechTransformer(
        voice="en-US-AriaNeural",  # or any supported voice
        rate="+0%",               # default rate
        pitch="+0Hz"              # default pitch
    )

    # Generate the voiceover
    tts_transformer.generate_voiceover(script_text, output_path)
