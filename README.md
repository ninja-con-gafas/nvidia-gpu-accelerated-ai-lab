# NVIDIA GPU Accelerated AI Lab

A GPU-accelerated AI lab environment built on top of **NVIDIA GPU-ready base images**.
This project is designed to be **modular and extensible**, enabling you to build tailored environments for a wide variety of AI models by layering **packs** on top of the appropriate NVIDIA base image.

**Packs** are lightweight overlays that install only the AI frameworks and dependencies needed for a specific model. This avoids bloating the base image while keeping environments compatible.

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

This project requires specifying the base NVIDIA GPU-ready image tag. Create an `.env` file in the root directory with the following variables:

You can customise your build via the `.env` variables:

* `BASE_IMAGE_TAG`: Base NVIDIA GPU-enabled image.
* `PACKS`: Comma-separated list of packs to include.
* `IMAGE_NAME`: Image name for the built image (Do not specify any tag).

For Jupyter server, set:

* `JUPYTER_ALLOW_UNAUTHENTICATED_ACCESS`: Allow access without login (default: `False`).
* `JUPYTER_DISABLE_CHECK_XSRF`: Disable Jupyter’s XSRF protection (default: `False`).
* `JUPYTER_USE_REDIRECT_FILE`: Extra arguments passed to `jupyter server`.
* `JUPYTER_TOKEN`: Token for authentication (default: empty).


```bash
BASE_IMAGE_TAG=
JUPYTER_ALLOW_UNAUTHENTICATED_ACCESS=
JUPYTER_DISABLE_CHECK_XSRF=
JUPYTER_TOKEN=
JUPYTER_USE_REDIRECT_FILE=
PACKS=
IMAGE_NAME=
```

> `BASE_IMAGE_TAG` and `IMAGE_NAME` must be set in the  `.env` otherwise `build.sh` will raise an error and exit.

---

## Catalogue

This catalogue guides which base image you should choose depending on the AI model you wish to run.  
Only *Ubuntu-based images* are supported.

---

### nvidia/cuda:[cuda_version]-cudnn[version]-devel-ubuntu[version]

For minimal GPU runtime and manual installation of frameworks.

- **Pre-installed libraries** (versions as per the image specifications):
  - CUDA Toolkit
  - cuDNN
  - Ubuntu

- **Packs**:
  - **llama.cpp** Refer to [llama.cpp](https://github.com/ggml-org/llama.cpp) for the list of supported AI models.

---

### pytorch/pytorch:[torch_version]-cuda[cuda_version]-cudnn[version]-devel

For PyTorch-based models with CUDA/cuDNN pre-configured.

- **Pre-installed libraries** (versions as per the image specifications):
  - PyTorch
  - CUDA Toolkit
  - cuDNN
  - Python

- **Packs**:
  - **qwen-image-edit** for Qwen Image Edit

---

> Select a minimal base image that already includes the frameworks required by your AI model. This reduces build complexity.

---

### Examples

Example for **llama.cpp**:

```bash
BASE_IMAGE_TAG=nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04
IMAGE_NAME=ninjacongafas/nvidia-ai-lab
PACKS=llama.cpp
```

Example for **Qwen-Image-Edit**:

```bash
BASE_IMAGE_TAG=pytorch/pytorch:2.8.0-cuda12.9-cudnn9-devel
IMAGE_NAME=ninjacongafas/nvidia-ai-lab
PACKS=qwen-image-edit
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
  -p 8888:8888 \
  -v <your-workspace>:/home/ai-lab/workspace:z \
  <your-image-tag>
```

You can override the entrypoint to run arbitrary commands inside the container instead of Jupyter server.

---

## Workspace

The container mounts your workspace at `/home/ai-lab/workspace` (or custom path if you change `WORKSPACE`), owned by the container user `ai-lab`.

Ports exposed:

* `8888`: Jupyter server

---