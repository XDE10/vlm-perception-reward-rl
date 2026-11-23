"""Prompt/image preparation used for the 150-step measurements.

Extracted from the locally adapted Shuffle-R1 evaluator. See UPSTREAM-LICENSE.
"""
import math
import os
from typing import Dict, List, Tuple

from PIL import Image


def load_image(image_path: str, min_pixels: int, max_pixels: int) -> Image.Image:
    """Load and preprocess an image"""
    try:
        # image = Image.open(image_path).convert("RGB")
        image = Image.open(image_path)
        if image.mode == "P":
            image = image.convert("RGBA")  # first handle palette+transparency
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")   # discard alpha channel
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize if too large or too small
        if (image.width * image.height) > max_pixels:
            resize_factor = math.sqrt(max_pixels / (image.width * image.height))
            width, height = int(image.width * resize_factor), int(image.height * resize_factor)
            image = image.resize((width, height))

        if (image.width * image.height) < min_pixels:
            resize_factor = math.sqrt(min_pixels / (image.width * image.height))
            width, height = int(image.width * resize_factor), int(image.height * resize_factor)
            image = image.resize((width, height))

        return image
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return None


def prepare_prompts(dataset_name: str, samples: List[Dict], args) -> Tuple[List[Dict], List[Dict]]:
    """Prepare prompts for all samples"""
    prompts = []
    metadata = []

    for item in samples:
        image_path = item.get("image_path")
        if isinstance(image_path, str):
            # Skip if image doesn't exists
            if not os.path.exists(image_path):
                continue
            # Load image
            image = load_image(image_path, args.min_pixels, args.max_pixels)
        elif isinstance(image_path, Image.Image):
            image = image_path
        else:
            image = None

        if image is None:
            continue

        # Create prompt
        prompt_text = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{args.system_prompt} <|vision_start|><|image_pad|><|vision_end|>{item['question']}<|im_end|>\n<|im_start|>assistant\n"

        prompts.append({
            "prompt": prompt_text,
            "multi_modal_data": {"image": image},
        })

        metadata.append({
            "dataset": dataset_name,
            "id": item["id"],
            "question": item["question"],
            "answer": item["answer"],
            "prompt": prompt_text,
            **{k: v for k, v in item.items() if k not in ["image_path", "image", "dataset", "id", "question", "answer"]}
        })

    return prompts, metadata
