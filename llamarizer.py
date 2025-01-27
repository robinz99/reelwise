#!pip install --quiet bitsandbytes
#!pip install --quiet --upgrade transformers
#!pip install --quiet --upgrade accelerate
#!pip install --quiet sentencepiece
#!pip install --quiet peft

#!pip install transformers bitsandbytes accelerate

import torch
import json

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

    def extract_key_concepts(self, transcript):
        """
        Extract key concepts from the given transcript using a system message
        and a user message. Returns the full pipeline output.
        """
        pipe = self._create_pipeline()

        messages_concepts = [
            {
                "role": "system",
                "content": (
                    "You are an expert in summarizing educational content. Your task is to extract key concepts or keywords from the provided "
                    "transcript of an educational lecture. Focus only on the most important and relevant ideas, terms, or phrases that are "
                    "essential to understanding the content. Do not generate a script or summary, only output a list of key concepts identified "
                    "from the transcript. Your output should be strictly a JSON array of the key concepts, without any extra commentary or explanation. "
                    "The key concepts should be terms or phrases that capture the essence of the lecture."
                ),
            },
            {
                "role": "user",
                "content": f"Here is the transcript of the lecture: [{transcript}]",
            },
        ]

        outputs_concepts = pipe(
            messages_concepts,
            max_new_tokens=64,
            do_sample=True
        )

        return outputs_concepts

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
                    "You are an expert video script writer specializing in educational content. "
                    "Your task is to create engaging and concise video scripts that explain complex topics in a simple and clear manner. "
                    "The user will provide a transcript of an educational lecture or material. "
                    "From this transcript, you will extract key concepts or keywords and generate a short, engaging script that explains these key ideas in a compelling way. "
                    "You ONLY produce text for the script, written with an educational tone and in a conversational and accessible style suitable for a short video. "
                    "Do not reference the video footage, audio, or other non-narrative elements in your response. "
                    "Your script must not exceed 200 words. Focus on clarity, brevity, and engagement. "
                    "Output your response in a strictly parsable JSON format, with the script under the key 'script'. "
                    "For example: {\"script\": \"Did you know that ... ?\"}"
                ),
            },
            {
                "role": "user",
                "content": f"Here is the transcript of the lecture: [{transcript}]",
            },
        ]

        outputs_script = pipe(
            messages_script,
            max_new_tokens=256,
            do_sample=True
        )

        return outputs_script
    
    def generate_image_prompts(self, script_json):
        """
        Given a JSON dictionary (like the output from generate_script) or a raw script string,
        create Bing-ready search terms for images that would fit each sentence of the script.

        - `script_json` can be either a dict with the key "script" or just a string of the script.
        - For each sentence in the script, produce one short search prompt.
        - Return a single list of search prompts in strictly JSON array format, e.g.: ["search prompt 1", "search prompt 2"].
        """
        # If script_json is actually a dictionary, extract the script text
        if isinstance(script_json, dict) and "script" in script_json:
            script_text = script_json["script"]
        else:
            # Otherwise assume the input is just a string script
            script_text = script_json

        pipe = self._create_pipeline()

        messages_prompts = [
            {
                "role": "system",
                "content": (
                    "You are a creative social media content planner. You specialize in selecting relevant images "
                    "to accompany short educational video reels on Instagram. You will receive a short script, "
                    "where each sentence should correspond to a distinct imagery concept. "
                    "Your task: for each sentence in the script, produce ONE Bing image search phrase. "
                    "These search terms should be concise, direct, and capture the core idea or metaphor "
                    "of each sentence, suitable for an Instagram educational reel. "
                    "Finally, return a strictly valid JSON array of search terms, "
                    "one array element per sentence. No extra commentary, no explanation—"
                    "just the JSON array. It must start with '[' and end with ']', "
                    "with a comma after each element except the last."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Script:\n{script_text}\n\n"
                    "Generate the Bing image search prompts now."
                ),
            },
        ]

        outputs_prompts = pipe(
            messages_prompts,
            max_new_tokens=128,
            do_sample=True
        )

        return outputs_prompts

