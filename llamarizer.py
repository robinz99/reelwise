#!pip install --quiet bitsandbytes
#!pip install --quiet --upgrade transformers
#!pip install --quiet --upgrade accelerate
#!pip install --quiet sentencepiece
#!pip install --quiet peft

#!pip install transformers bitsandbytes accelerate

import torch
import json
import time
import re

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import (
    LoraConfig,
    PeftModel,
    prepare_model_for_kbit_training,
    get_peft_model,
)

class LLaMarizer:
    def __init__(self, use_cuda=False):
        """
        Initialize configuration, model, tokenizer, and any other essentials.
        The `use_cuda` parameter decides whether to run on CPU or GPU.
        """
        # This helps reduce memory usage and speeds up computations, especially on GPUs.
        # "Eager" mode means that operations are executed immediately as they are called.
        self.attn_implementation = "eager"
        self.auth_token = ""
        
        if use_cuda:
            self.device_map = "auto"
            self.torch_dtype = torch.float16

            # QLoRA config (speeds up processing) - used only with CUDA
            self.bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=self.torch_dtype,
                bnb_4bit_use_double_quant=True,
            )

            # Load model with quantization config
            self.model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-3.2-1B-Instruct",
                device_map=self.device_map,
                attn_implementation="eager",
                use_auth_token=self.auth_token,
                quantization_config=self.bnb_config
            )
        else:
            self.device_map = {"": "cpu"}
            self.torch_dtype = torch.float32

            # Load model without quantization config
            self.model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-3.2-1B-Instruct",
                device_map=self.device_map,
                attn_implementation="eager",
                use_auth_token=self.auth_token,
            )

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Llama-3.2-1B-Instruct",
            use_auth_token=self.auth_token
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # LoRA config
        self.peft_config = LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=['up_proj', 'down_proj', 'gate_proj', 'k_proj', 'q_proj', 'v_proj', 'o_proj']
        )

        # Apply LoRA to the Model
        self.model = get_peft_model(self.model, self.peft_config)

    def _create_pipeline(self):
        """
        Create a text-generation pipeline with the configured model and tokenizer.
        """
        return pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=self.torch_dtype,
            device_map=self.device_map,
        )

    def generate_script(self, transcript):
        """
        Generate a short educational video script (JSON format) from the given transcript.
        Returns the full pipeline output.
        """
        pipe = self._create_pipeline()

        messages_script = [
            {
                "role": "system",
                "content": (
                    "You're an expert video script writer specializing in educational content. Your task is to "
                    "create engaging and concise text scripts for Instagram Reels that explain complex topics "
                    "in a simple, clear manner. The user will provide a transcript of an educational lecture or "
                    "material. Be aware that the transcript is imperfect, there will be mistakes in it. From this transcript, you will extract the key concepts and create one short, "
                    "engaging script. The script should be written with an educational tone, conversational style, "
                    "and suitable for a short video. It must end in a complete sentence, ensuring there are no "
                    "unfinished or incomplete thoughts. Your output must be only the script as a single string - "
                    "no JSON, no commentary, and no additional formatting. Do not include any timestamps, it should "
                    "be in the style of a transcript, ready to be read by one narrator. You ONLY produce text that "
                    "will be read by a voice actor for a video. The user will give you the description of the video "
                    "they want you to make and from that, you will write the script. Make sure to directly write "
                    "the script in response to the lecture transcript provided by the user. Only include the text that will be narrated by the "
                    "voice actor. You will produce purely text, with no other textual elements than the script itself."
                    "Keep your answer concise and short, with a maximum of 100 words."
                ),
            },
            {
                "role": "user",
                "content": f"Here is the transcript of the lecture: [{transcript}]",
            },
        ]

        outputs_script = pipe(
            messages_script,
            max_new_tokens=512,
            do_sample=True
        )

        return outputs_script
    
    def generate_bing_search_term(self, script_text):
        """
        Given a string representing the script, create Bing-ready search terms 
        for images that would fit each sentence of the script.

        Returns a single string which should be a strictly valid JSON array
        of search terms, e.g.: ["search prompt 1", "search prompt 2"].
        """
        pipe = self._create_pipeline()

        messages_prompts = [
            {
                "role": "system",
                "content": (
                    "You are a creative social media content planner. You specialize in selecting relevant images "
                    "to accompany short educational video reels on Instagram. You will receive exactly one sentence of a reel script. "
                    "Your task: for this sentence from the script, produce ONE Bing image search term to find a fitting image. "
                    "This search term should be concise, direct, and capture the core idea or metaphor "
                    "of each sentence, suitable for an Instagram educational reel."
                    "It should help the viewer understand the concept mentioned in the sentence."
                    "Return only the search term, in exactly the format that can be pasted into the Bing search bar."
                    "No extra commentary, no explanation, just the Bing search term."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Sentence:\n{script_text}\n\n"
                    "Generate the Bing image search term now."
                ),
            },
        ]

        outputs_prompts = pipe(
            messages_prompts,
            max_new_tokens=512,
            do_sample=True
        )

        # The pipeline's default return is a list of dicts with the key "generated_text"
        # e.g., [{"generated_text": "..."}].
        # We only need the string from the first item in that list:
        raw_response = outputs_prompts[0]["generated_text"][-1]["content"]

        # Return just the single string
        return raw_response
    
    def generate_multiple_bing_search_terms(self, sentences):
        """
        Takes a list of sentences, calls `generate_bing_search_term` on each,
        and returns a list of strings containing the Bing search terms.
        """
        results = []
        for sentence in sentences:
            search_term = self.generate_bing_search_term(sentence)
            results.append(search_term)
        return results

    def is_valid_format(self, response):
        try:
            parsed_output = json.loads(response)
            return True
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
        return False

    def generate_scripts_until_valid(self, transcript, retries=10, delay=2):
        attempts = 0
        while attempts < retries:
            outputs_script = self.generate_script(transcript)
            raw_response = outputs_script[0]["generated_text"]
            
            if self.is_valid_format(raw_response):
                return raw_response
            
            print(f"Attempt {attempts + 1} failed, retrying...")
            time.sleep(delay)
            attempts += 1

        raise ValueError("Failed to generate a valid script after multiple attempts")
    
    def process_script(self, script):
        """
        Takes a string input:
        1) If there is a colon in the first sentence, remove everything up to and including that colon.
        2) Split the remaining text into a list of sentences.
        """
        # First check for colon in the text before first period/question mark/exclamation
        first_sentence_end = re.search(r'[.?!]', script)
        if first_sentence_end:
            first_part = script[:first_sentence_end.start()]
            rest = script[first_sentence_end.start():]
        else:
            first_part = script
            rest = ""
            
        # If first part contains colon, remove everything before it
        if ':' in first_part:
            _, after_colon = first_part.split(':', 1)
            script = after_colon.strip() + rest
            
        # Split into sentences, keeping the punctuation
        sentences = [sent.strip() for sent in re.findall(r'[^.!?]+[.!?]', script)]
        
        return sentences

