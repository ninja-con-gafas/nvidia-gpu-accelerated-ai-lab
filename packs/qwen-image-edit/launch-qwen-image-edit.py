#!/usr/bin/env python3

"""
Qwen Image Edit Pipeline with GGUF support.

Parameters:
    User-provided:
        --models_dir (str): Path to the GGUF models root directory.
            Expected directory structure:
                models/
                ├── diffusion_models/             -> contains *.gguf (Download from https://huggingface.co/QuantStack/Qwen-Image-GGUF)
                ├── text_encoders/                -> contains *.gguf (Download from https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct)
                    └── Qwen2.5-VL-7B-Instruct/   -> contains tokenizer configuration files downloaded from the same page as above.
        --image (str): Path to the input image.
        --prompt (str): Prompt for editing.
    Auto-detected:
        - device (str): "cuda" (GPU required).
        - dtype (torch.dtype): bfloat16 for inference.

Raises:
    FileNotFoundError: If any required model file does not exist.
    RuntimeError: If GPU is not available or model loading fails.
"""

import argparse
import os
import torch
from diffusers import AutoencoderKLQwenImage, GGUFQuantizationConfig, QwenImageEditPipeline, QwenImageTransformer2DModel
from PIL import Image
from transformers import AutoTokenizer

def choose_gguf_file(directory: str, component: str) -> str:
    """
    Prompt user to select a GGUF file if multiple exist in the directory.
    
    Parameters:
        directory (str): Path to the directory containing GGUF files.
        component (str): Name of the model component (for user prompts).
        
    Returns:
        str: Path to the selected GGUF file.
    """

    gguf_files = [f for f in os.listdir(directory) if f.endswith(".gguf")]
    if not gguf_files:
        raise FileNotFoundError(f"No GGUF file found in {directory}")

    if len(gguf_files) == 1:
        return os.path.join(directory, gguf_files[0])

    print(f"\nMultiple GGUF files found for {component} in {directory}:")
    for idx, fname in enumerate(gguf_files, 1):
        print(f"  [{idx}] {fname}")
    while True:
        try:
            choice = int(input(f"Select {component} model [1-{len(gguf_files)}]: ").strip())
            if 1 <= choice <= len(gguf_files):
                return os.path.join(directory, gguf_files[choice - 1])
        except ValueError:
            pass
        print("Invalid choice, please try again.")

def resolve_model_paths(base_dir: str) -> dict:
    """
    Return dictionary of expected component model paths from the base directory.

    Parameters:
        base_dir (str): Path to the GGUF models root directory.

    Returns:
        dict: Dictionary with keys 'diffusion_models', 'text_encoder', and 'vae' mapping to their respective file paths.
    """

    return {
        "diffusion_models": choose_gguf_file(os.path.join(base_dir, "diffusion_models"), "diffusion_models"),
        "text_encoder": choose_gguf_file(os.path.join(base_dir, "text_encoders"), "text encoder")
    }

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the Qwen Image Edit Pipeline with GGUF support.

    Returns:
        argparse.Namespace: Parsed arguments including:
            - models_dir (str): Path to GGUF models directory.
            - image (str): Path to input image.
            - prompt (str): Text prompt for editing.
            - negative_prompt (str): Negative prompt.
            - true_cfg_scale (float): CFG scale value.
            - num_inference_steps (int): Number of inference steps.
            - seed (int): Random seed.
    """

    parser = argparse.ArgumentParser(description="Qwen Image Edit Pipeline (GGUF)")
    parser.add_argument("--models_dir", type=str, required=True, help="Path to GGUF models directory")
    parser.add_argument("--image", type=str, required=True, help="Path to input image (e.g., ./input.png)")
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt for image editing")
    parser.add_argument("--negative_prompt", type=str, default=" ", help="Negative prompt (default blank)")
    parser.add_argument("--true_cfg_scale", type=float, default=4.0, help="CFG scale (default: 4.0)")
    parser.add_argument("--num_inference_steps", type=int, default=50, help="Inference steps (default: 50)")
    parser.add_argument("--seed", type=int, default=0, help="Random seed (default: 0)")
    return parser.parse_args()

def main() -> None:
    """
    Main entry point for the Qwen Image Edit Pipeline with GGUF support.

    Workflow:
        - Parse command-line arguments.
        - Resolve GGUF model paths (diffusion models and text encoder).
        - Load transformer, text encoder, and VAE.
        - Initialize the Qwen Image Edit pipeline.
        - Run inference with the given prompt and input image.
        - Save the edited image to disk as `output_image_edit.png`.

    Raises:
        RuntimeError: If CUDA device is not available.
        FileNotFoundError: If required model files are missing.
    """

    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA device not available. GPU is required.")

    paths = resolve_model_paths(args.models_dir)

    transformer = QwenImageTransformer2DModel.from_single_file(
        paths["diffusion_models"],
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        torch_dtype=torch.bfloat16,
        config="Qwen/Qwen-Image-Edit",
        subfolder="transformer",
        device_map="auto")
    
    """
    Hugging Face Transformers currently does not support GGUF-based text encoders. 
    Attempting to initialise models with architectures such as `qwen2vl` results in:

        ValueError: GGUF model with architecture qwen2vl is not supported yet.

    References:
        - vLLM issue: https://github.com/vllm-project/vllm/issues/20253
        - Transformers issue: https://github.com/huggingface/transformers/issues/40049
        - Transformers PR: https://github.com/huggingface/transformers/pull/40058
    """

    text_encoder = AutoTokenizer.from_pretrained(
        os.path.join(os.path.dirname(paths["text_encoder"]), "Qwen2.5-VL-7B-Instruct"),
        gguf_file=paths["text_encoder"])

    vae = AutoencoderKLQwenImage.from_pretrained(
        "Qwen/Qwen-Image-Edit",
        subfolder="vae",
        torch_dtype=torch.bfloat16).to("cuda:0")

    pipeline = QwenImageEditPipeline.from_pretrained(
        "Qwen/Qwen-Image-Edit",
        transformer=transformer,
        text_encoder=text_encoder,
        vae=vae,
        torch_dtype=torch.bfloat16)

    print("Pipeline loaded successfully.")

    image = Image.open(args.image).convert("RGB")
    generator = torch.manual_seed(args.seed)

    inputs = {
        "image": image,
        "prompt": args.prompt,
        "negative_prompt": args.negative_prompt,
        "true_cfg_scale": args.true_cfg_scale,
        "num_inference_steps": args.num_inference_steps,
        "generator": generator,
    }

    with torch.inference_mode():
        output = pipeline(**inputs)
        output_image = output.images[0]
        output_image.save("output_image_edit.png")
        print("image saved at", os.path.abspath("output_image_edit.png"))

if __name__ == "__main__":
    main()
