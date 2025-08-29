# NVIDIA GPU Accelerated AI Lab

A GPU-accelerated AI lab environment based on **NVIDIA Triton Inference Server** that also supports **llama.cpp** for rapid AI model experimentation and deployment.

This project provides two modes of container images:

* **Development mode (`DEV=true`)**: includes Jupyter server, developer tools, CLI utilities, and debugging helpers.
* **Deployment mode (`DEV=false` default)**: runtime-only variant of the development image.

---

## Features

* **NVIDIA GPU Acceleration** (CUDA-enabled)
* **Backends**:
  * [Triton Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/archives/triton_inference_server_1120/triton-inference-server-guide/docs/index.html#)
  * [llama.cpp](https://github.com/ggml-org/llama.cpp)
* **Developer tools** (installed only in `DEV=true` mode):
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
    * `ipykernel`
    * `jq`
    * `jupyter-server-proxy`
    * `jupyterlab`
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

---

## Requirements

* NVIDIA GPU with drivers installed
* [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html)
* Podman or Docker

---

## Base Image Configuration

This project requires specifying the base NVIDIA Triton Inference Server image tag. Create an `.env` file in the root directory with the following variables:

```bash
# Enable development mode (default: false)
DEV=true

# Base NVIDIA Triton Inference Server image (default: nvcr.io/nvidia/tritonserver:25.05-vllm-python-py3)
IMAGE_NAME="nvcr.io/nvidia/tritonserver:25.05-vllm-python-py3"

# Tag for the built image (default: ninjacongafas/nvidia-gpu-accelerated-ai-lab:latest)
TAG="ninjacongafas/nvidia-gpu-accelerated-ai-lab:20250829"
````

If `.env` is not provided, `build.sh` will fall back to the default values shown above.

---

## Building Images

The build process is managed by `build.sh`, which automatically reads `.env` and constructs the proper build arguments. To build the image, run:

```bash
bash build.sh
```

The script will detect whether Podman or Docker is installed and use it automatically.
You can customise your build via the `.env` variables:

* `DEV=true` for development mode (includes tools and Jupyter)
* `DEV=false` for deployment mode
* `IMAGE_NAME` to override the default NVIDIA Triton image
* `TAG` to specify a custom image tag

---

## Running Containers

```bash
podman run -d \
  --rm \
  --init \
  --name nvidia-ai-lab \
  --gpus all \
  -p 8000-8002:8000-8002 \
  -p 8080:8080 \
  -p 8888:8888 \
  -v <your-workspace>:/workspace:z \
  <your-image-tag>
```

Attach from VS Code using the **Remote Containers** extension.

---

## Workspace

The container mounts your workspace at `/home/ai-lab/workspace` (or custom path if you change `WORKSPACE`), owned by the container user `ai-lab`.

Ports exposed:

* `8000-8002`: Triton Inference Server gRPC and HTTP
* `8080`: llama.cpp server HTTP
* `8888`: Jupyter server

---