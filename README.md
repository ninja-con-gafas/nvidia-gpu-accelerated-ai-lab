# NVIDIA GPU Accelerated AI Lab
[![Container Ready](https://img.shields.io/badge/container-ready-blue)]()
[![CUDA](https://img.shields.io/badge/CUDA-12.9-green)]()
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-orange)]()

A GPU-accelerated AI lab environment built on top of **NVIDIA GPU-ready base images**.
Designed to be **modular** and **extensible**, enabling you to build tailored environments for a wide variety of AI models by layering **packs** on top of a minimal, CUDA/cuDNN‑enabled base.

**Packs** are lightweight overlays that install only the AI frameworks and dependencies needed for a specific model. This avoids bloating the base image while keeping environments compatible.

---

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Base Image Configuration](#base-image-configuration)
4. [Catalogue](#catalogue)
5. [Quickstart](#quickstart)
6. [Building Images](#building-images)
7. [Running Containers](#running-containers)
8. [Workspace](#workspace)

---

## Features

* **NVIDIA GPU Acceleration** (CUDA-enabled with cuDNN support)
* **Developer tools included by default**:
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

These utilities form the common base for all environments.

---

## Requirements

* NVIDIA GPU and drivers installed on the host machine.
* [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html)
* Docker or Podman

---

## Base Image Configuration

Create a `.env` file in the root directory with the following variables:

* `BASE_IMAGE_TAG`: Base NVIDIA GPU-enabled image.
* `PACKS`: Comma-separated list of packs to include.
* `IMAGE_NAME`: Image name for the built image (Do not specify any tag).

```bash
BASE_IMAGE_TAG=
IMAGE_NAME=
PACKS=
```

---

### Example `.env`

```bash
BASE_IMAGE_TAG=nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04
IMAGE_NAME=ninjacongafas/nvidia-ai-lab
PACKS=llama.cpp,qwen-image-edit
```

> `BASE_IMAGE_TAG` and `IMAGE_NAME` must be set in the  `.env` otherwise `build.sh` will raise an error and exit.

---

## Catalogue

This catalogue guides which base image you should choose depending on the AI model you wish to run.  
Only *Ubuntu-based images* are supported.

---

| Base Image Format | Runtime Purpose | Pre-installed Libraries | Supported Packs |
|-------------------|------------------|--------------------------|------------------|
| `nvidia/cuda:[cuda_version]-cudnn[version]-devel-ubuntu[version]` | GPU runtime with manual framework installation | - CUDA Toolkit<br>- cuDNN<br>- Ubuntu | - [`llama.cpp`](https://github.com/ggml-org/llama.cpp)<br>Supports LLaMA-family models |
| `pytorch/pytorch:[torch_version]-cuda[cuda_version]-cudnn[version]-devel` | PyTorch-based models with CUDA/cuDNN pre-configured | - PyTorch<br>- CUDA Toolkit<br>- cuDNN<br>- Python | - `qwen-image-edit`<br>Supports Qwen Image Edit |

---

## Quickstart

```bash
git clone https://github.com/ninja-con-gafas/nvidia-gpu-accelerated-ai-lab.git
cd nvidia-gpu-accelerated-ai-lab

cat <<EOF > .env
BASE_IMAGE_TAG=nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04
IMAGE_NAME=nvidia-gpu-accelerated-ai-lab
PACKS=llama.cpp
EOF

bash build.sh

podman run -d \
  --rm \
  --init \
  --name ai-lab \
  --gpus all \
  -e JUPYTER_ALLOW_UNAUTHENTICATED_ACCESS=False \
  -e JUPYTER_ARGS= \
  -e JUPYTER_DISABLE_CHECK_XSRF=False \
  -e JUPYTER_TOKEN=passwd \
  -e JUPYTER_USE_REDIRECT_FILE=True \
  -p 8888:8888 \
  -v $(pwd)/workspace:/home/ai-lab/workspace:z \
  nvidia-gpu-accelerated-ai-lab_llama.cpp:latest
```

---

## Building Images

The build process is managed by `build.sh`, which automatically reads `.env` and constructs the proper build arguments.

To build the image, run:

```bash
bash build.sh
```

---

## Running Containers

```bash
podman run -d \
  --rm \
  --init \
  --name nvidia-ai-lab \
  --gpus all \
  -e JUPYTER_ALLOW_UNAUTHENTICATED_ACCESS=False \
  -e JUPYTER_ARGS= \
  -e JUPYTER_DISABLE_CHECK_XSRF=False \
  -e JUPYTER_TOKEN=passwd \
  -e JUPYTER_USE_REDIRECT_FILE=True \
  -p 8888:8888 \
  -v <your-workspace>:/home/ai-lab/workspace:z \
  <your-image-tag>
```

> You can override the entrypoint to run arbitrary commands inside the container instead of Jupyter server.

```bash
podman run --rm --gpus all <your-image-tag> bash
```

---

## Workspace

- Mounted at `/home/ai-lab/workspace` (or custom via `WORKSPACE` env var)
- Owned by container user `ai-lab`
- Port **8888** exposed for Jupyter

---