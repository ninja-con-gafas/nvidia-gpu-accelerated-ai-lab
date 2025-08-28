# NVIDIA GPU Accelerated AI Lab

A GPU-accelerated AI lab environment based on **NVIDIA Triton Inference Server** that also supports **llama.cpp** for rapid AI model experimentation and deployment.

This project provides two variants of container images:

* **Development image [`Dockerfile.dev`](Dockerfile.dev)**: includes Jupyter, developer tools, CLI utilities, and debugging helpers.
* **Deployment image [`Dockerfile.deploy`](Dockerfile.deploy)**: a runtime variant of the `dev` image.

---

## Features

* **NVIDIA GPU Acceleration** (CUDA-enabled)
* **Multiple model formats**: `safetensors`, `gguf`, `pt`, `onnx`, TensorRT engines
* **Backends**:
  * [Triton Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/archives/triton_inference_server_1120/triton-inference-server-guide/docs/index.html#)
  * [vLLM](https://github.com/vllm-project/vllm)
  * [llama.cpp](https://github.com/ggml-org/llama.cpp)
* **Developer tools**:
    * `build-essential`
    * `cmake`
    * `curl`
    * `dnsutils`
    * `findutils`
    * `git`
    * `htop`
    * `iotop`
    * `iproute2`
    * `iputils-ping`
    * `jq`
    * `less`
    * `libcurl4-openssl-dev`
    * `libgomp1`
    * `lsof`
    * `nano`
    * `ncdu`
    * `net-tools`
    * `nvtop`
    * `procps`
    * `python3-pip`
    * `ripgrep`
    * `strace`
    * `telnet`
    * `traceroute`
    * `tree`
    * `vim`
    * `wget`
    * `yq`
> *Developer tools are installed only in the development image [`Dockerfile.dev`](Dockerfile.dev).

---

## Requirements

* NVIDIA GPU with drivers installed
* [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html)
* Podman or Docker

---

## Base Image Configuration

This project requires specifying the base NVIDIA image tag.
Create an `.env` file in the root directory with:

```bash
IMAGE_NAME=nvcr.io/nvidia/tritonserver:25.08-vllm-python-py3
```

If `.env` is not provided, the Dockerfile will fall back to its default image `nvcr.io/nvidia/tritonserver:25.08-vllm-python-py3`.

---

## Building Images

```bash
podman build -t ninjacongafas/nvidia-gpu-accelerated-ai-lab:dev -f Dockerfile.<> .
```

---

## Running Containers

```bash
podman run -d --rm \
    --name nvidia-ai-lab \
    --gpus all \
    -p 8000-8002:8000-8002 \
    -p 8080:8080 \
    -p 8888:8888 \
    -v <your-workspace>:/workspace \
    <your-image-tag>
```

Attach from VS Code using the **Remote Containers** extension.

---

Start llama.cpp server manually inside:

```bash
llama-server -hf TheBloke/Llama-2-7B-GGUF
```

---