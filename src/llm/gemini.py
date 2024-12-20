from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import os

class Gemini:
    def __init__(
        self, 
        system_prompt,
        model_name='gemini-1.5-flash',
        generation_config=None, 
        api_key=None
    ):
        self._model = self._setup(system_prompt, model_name, generation_config, api_key)

    def _setup(
        self, 
        system_prompt,
        model_name, 
        generation_config=None, 
        api_key=None
    ):
        if api_key is not None:
            genai.configure(api_key=api_key)
        else:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        if generation_config is None:
            generation_config = {
                'temperature': 0.2,
                'max_output_tokens': 1000
            }
        return genai.GenerativeModel(
            model_name,
            system_instruction=system_prompt,
            generation_config = generation_config,
            safety_settings=safety_settings
    )
    
    def generate(self, prompt):
        return self._model.generate_content(prompt).text