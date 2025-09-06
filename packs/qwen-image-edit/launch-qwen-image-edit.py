#!/usr/bin/env python3

"""
A Gradio application for image editing using Qwen GGUF models (GPU-only, multi-GPU supported).

Parameters:
    User-provided:
        - models_dir (str): Path to the GGUF models root directory.
        Expected directory structure:
            models/
            ├── editor/        -> contains *.gguf (Download from https://huggingface.co/QuantStack/Qwen-Image-GGUF/tree/main)
            ├── text_encoder/  -> contains *.gguf (Download from https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/tree/main)
    Auto-detected:
        - device (str): Always "cuda" (must have GPU).
        - dtype (torch.dtype): Always bfloat16 for GPU inference.

Returns:
    Gradio UI for editing input images with user-provided prompts.

Raises:
    FileNotFoundError: If any required model file does not exist.
    RuntimeError: If GPU is not available or model loading fails.
"""

import os
import torch
from diffusers import AutoencoderKLQwenImage, GGUFQuantizationConfig, QwenImageEditPipeline, QwenImageTransformer2DModel
from gradio import Blocks, Button, Column, Dataset, Image, Markdown, Row, Slider, Textbox
from transformers import Qwen2_5_VLForConditionalGeneration

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
        dict: Dictionary with keys 'editor', 'text_encoder', and 'vae' mapping to their respective file paths.
    """

    return {
        "editor": choose_gguf_file(os.path.join(base_dir, "editor"), "editor"),
        "text_encoder": choose_gguf_file(os.path.join(base_dir, "text_encoder"), "text encoder")
    }

def launch_image_edit_app(models_dir: str, dtype: torch.bfloat16) -> None:
    """
    Launch the Gradio-based image editing application using Qwen GGUF models.

    Parameters:
        models_dir (str): Path to directory containing the GGUF model subfolders.
        dtype (torch.dtype): Torch data type (always bfloat16 here).

    Returns:
        None
    """

    paths = resolve_model_paths(models_dir)

    transformer = QwenImageTransformer2DModel.from_single_file(
        paths["editor"],
        quantization_config=GGUFQuantizationConfig(compute_dtype=dtype),
        torch_dtype=dtype,
        config="Qwen/Qwen-Image-Edit",
        subfolder="transformer",
        device_map="auto"
    )

    # Here lies the problem, need a way to run the text encoder in GGUF format.
    text_encoder = Qwen2_5_VLForConditionalGeneration.from_single_file(
        paths["text_encoder"],
        quantization_config=GGUFQuantizationConfig(compute_dtype=dtype),
        torch_dtype=dtype,
        device_map="auto"
    )

    vae = AutoencoderKLQwenImage.from_pretrained(
        "Qwen/Qwen-Image-Edit",
        subfolder="vae",
        torch_dtype=dtype
    ).to("cuda:0")

    pipe = QwenImageEditPipeline.from_pretrained(
        None,
        transformer=transformer,
        text_encoder=text_encoder,
        vae=vae,
        torch_dtype=dtype
    )

    if hasattr(pipe, "enable_sequential_cpu_offload"):
        pipe.enable_sequential_cpu_offload = lambda *args, **kwargs: None

    def generate_image(image, prompt: str, neg_prompt: str, guidance_scale: float, num_steps: int):
        if image is None or prompt.strip() == "":
            return None
        result = pipe(
            image=image,
            prompt=prompt,
            true_cfg_scale=guidance_scale,
            negative_prompt=neg_prompt,
            num_inference_steps=num_steps,
        ).images[0]
        return result

    sample_prompts = [
        ['Turn the image into Pixar style.'],
        ['Turn the image into Ghibli style.'],
        ['Turn the image into a Van Gogh painting.'],
    ]

    block = Blocks(title="GGUF Image Editor").queue()
    with block:
        Markdown("## Qwen Image Edit")
        with Row():
            with Column():
                input_image = Image(type="pil", label="Input Image")
                prompt = Textbox(label="Prompt", placeholder="Enter your prompt here", value="")
                neg_prompt = Textbox(label="Negative Prompt", value=" ", visible=False)
                quick_prompts = Dataset(samples=sample_prompts, label="Sample Prompt",
                                        samples_per_page=1000, components=[prompt])
                quick_prompts.click(lambda x: x[0], inputs=[quick_prompts], outputs=prompt,
                                    show_progress=False, queue=False)
                submit_btn = Button("Generate")
                num_steps = Slider(minimum=4, maximum=100, value=8, step=1, label="Steps")
                guidance = Slider(minimum=0.0, maximum=10.0, value=1, step=0.1, label="Guidance Scale")
            with Column():
                output_image = Image(type="pil", label="Output Image")
        submit_btn.click(fn=generate_image,
                         inputs=[input_image, prompt, neg_prompt, guidance, num_steps],
                         outputs=output_image)
    block.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    models_dir: str = input("Enter the path to the GGUF models directory: ").strip()

    if not os.path.isdir(models_dir):
        raise FileNotFoundError(f"The specified directory does not exist: {models_dir}")

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required but not available.")

    device: str = "cuda"
    dtype = torch.bfloat16

    print(f"Models directory: {models_dir}")
    print(f"Device detected: {device}")
    print(f"torch version: {torch.__version__}")
    print(f"dtype using: {dtype}")
    print(f"running with {torch.cuda.device_count()} GPU(s)")
    for idx in range(torch.cuda.device_count()):
        print(f"    GPU {idx}: {torch.cuda.get_device_name(idx)}")

    launch_image_edit_app(models_dir, dtype)
