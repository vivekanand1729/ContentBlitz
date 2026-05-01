import os
import uuid
import requests
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage
from openai import OpenAI
from src.core.config import config
from src.core.llm import get_llm
from src.core.state import ContentState


PROMPT_ENHANCER = """You are an expert at writing image generation prompts for marketing content.

Content topic: {query}
Context: {context}

Write a single, highly detailed image prompt (150-200 words) that:
- Creates a professional marketing/business visual
- Specifies art style (photorealistic, digital art, flat design, 3D render, etc.)
- Describes composition, colors, lighting, and mood
- Is suitable for content marketing (blog headers, social media, presentations)
- Contains NO text, typography, or words in the image

Return ONLY the image prompt. Nothing else."""


class ImageGeneratorAgent:
    def __init__(self):
        self.prompt_llm = get_llm(max_tokens=512)
        self.openai_client = None
        if config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        Path(config.IMAGES_DIR).mkdir(exist_ok=True)

    def _enhance_prompt(self, query: str, context: str) -> str:
        prompt = PROMPT_ENHANCER.format(query=query, context=context[:300])
        try:
            response = self.prompt_llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception:
            return f"Professional marketing image about {query}, photorealistic, clean composition, vibrant colors, high quality"

    def _generate_and_save(self, prompt: str) -> tuple[str, str]:
        model = config.IMAGE_MODEL
        size = config.IMAGE_SIZE
        kwargs: dict = {"model": model, "prompt": prompt, "size": size, "n": 1}

        # dall-e-3 supports quality; dall-e-2 does not
        if model == "dall-e-3":
            kwargs["quality"] = config.IMAGE_QUALITY

        try:
            response = self.openai_client.images.generate(**kwargs)
        except Exception as e:
            err = str(e)
            # Fall back to dall-e-2 if this project lacks dall-e-3 access
            if model == "dall-e-3" and ("403" in err or "model_not_found" in err or "does not have access" in err):
                # dall-e-2 only supports up to 1024x1024
                safe_size = size if size in ("256x256", "512x512", "1024x1024") else "1024x1024"
                response = self.openai_client.images.generate(
                    model="dall-e-2",
                    prompt=prompt[:1000],  # dall-e-2 has a 1000-char prompt limit
                    size=safe_size,
                    n=1,
                )
            else:
                raise

        url = response.data[0].url
        filename = f"{uuid.uuid4().hex[:12]}.png"
        local_path = os.path.join(config.IMAGES_DIR, filename)
        img_bytes = requests.get(url, timeout=30).content
        with open(local_path, "wb") as f:
            f.write(img_bytes)
        return url, local_path

    def run(self, state: ContentState) -> dict:
        query = state.get("query", "")
        research = state.get("research_results", {})
        context = research.get("analysis", query)

        enhanced_prompt = self._enhance_prompt(query, context)

        if not self.openai_client:
            msg = (
                f"**Image Generation**\n\n"
                f"⚠️ OpenAI API key not configured — image generation unavailable.\n\n"
                f"**Optimized Prompt (copy into DALL-E or Midjourney):**\n\n{enhanced_prompt}"
            )
            return {
                "generated_content": msg,
                "content_format": "image",
                "image_urls": [],
                "content_metadata": {
                    "content_type": "Image",
                    "enhanced_prompt": enhanced_prompt,
                },
                "messages": [AIMessage(content=msg)],
            }

        try:
            url, local_path = self._generate_and_save(enhanced_prompt)
            msg = (
                f"**Generated Image** ✓\n\n"
                f"Saved to: `{local_path}`\n\n"
                f"**Optimized Prompt Used:**\n{enhanced_prompt}"
            )
            image_urls = [local_path]
        except Exception as e:
            msg = (
                f"**Image Generation Failed**\n\n"
                f"Error: {str(e)}\n\n"
                f"**Optimized Prompt (ready for manual use):**\n\n{enhanced_prompt}"
            )
            image_urls = []

        return {
            "generated_content": msg,
            "content_format": "image",
            "image_urls": image_urls,
            "content_metadata": {
                "content_type": "AI Generated Image",
                "enhanced_prompt": enhanced_prompt,
            },
            "messages": [AIMessage(content=msg)],
        }
