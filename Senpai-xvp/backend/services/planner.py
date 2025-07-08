import openai
import os
import logging
from typing import List, Optional

class Planner:
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-4"
    logger = logging.getLogger(__name__)

    @classmethod
    def initialize(cls, openai_api_key: str) -> None:
        """Initializes the Planner class, loading the OpenAI API key."""
        if not openai_api_key:
            cls.logger.error("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
            raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        openai.api_key = openai_api_key
        cls.openai_api_key = openai_api_key
        cls.logger.info("Planner service initialized.")

    @classmethod
    def generate_plan(cls, task: str, context: str, dom: str = "", screenshot: Optional[bytes] = None) -> List[str]:
        """
        Generates a plan based on the given task, context, DOM, and screenshot using OpenAI's GPT-4.
        """
        try:
            prompt = f"You are an expert web automation agent. Your goal is to create plans to satisfy the user. Task: {task}
Context: {context}"
            if dom:
                prompt += f"

Here is the DOM: {dom}"
                prompt += f"
Based on the DOM, what elements are available for me?"

            if screenshot:
                # TODO: Implement OCR or visual analysis of the screenshot
                prompt += "
[Screenshot: Implement visual analysis]"

            prompt += "

What is the step by step plan?"
            response = openai.Completion.create(
                engine=cls.model_name,
                prompt=prompt,
                max_tokens=250, # Increased max_tokens
                n=1,
                stop=None,
                temperature=0.7,
            )
            plan = response.choices[0].text.strip().split("
")
            cls.logger.info(f"Generated plan: {plan}")
            return plan
        except openai.error.OpenAIError as e:
            cls.logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {e}") # Re-raise to notify the caller
        except Exception as e:
            cls.logger.exception("Error generating plan")
            raise Exception(f"Error generating plan: {e}")
