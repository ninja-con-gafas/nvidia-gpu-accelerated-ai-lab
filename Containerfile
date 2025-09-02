ARG BASE_IMAGE_TAG=ninjacongafas/nvidia-gpu-accelerated-ai-lab:latest
FROM ${BASE_IMAGE_TAG}
LABEL maintainer="ninja-con-gafas <el.ninja.con.gafas@gmail.com>" \
      org.opencontainers.image.source="https://github.com/ninja-con-gafas/nvidia-gpu-accelerated-ai-lab.git" \
      org.opencontainers.image.description="NVIDIA GPU Accelerated AI Lab Base Image" \
      org.opencontainers.image.licenses="AGPL-3.0"

ARG UID=1001
ARG GID=1001
ARG USERNAME=ai-lab
ARG WORKSPACE=/home/${USERNAME}/workspace

ENV DEBIAN_FRONTEND=noninteractive
ENV USERNAME=${USERNAME}
ENV HOME=/home/${USERNAME}
ENV WORKSPACE=${WORKSPACE}

RUN groupadd -g ${GID} ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME} && \
    mkdir -p ${WORKSPACE} && \
    chown -R ${UID}:${GID} ${WORKSPACE}

RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \
        build-essential \
        cmake \
        curl \
        dnsutils \
        findutils \
        git \
        htop \
        iotop \
        iproute2 \
        iputils-ping \
        jq \
        less \
        libcurl4-openssl-dev \
        libgomp1 \
        lsof \
        nano \
        ncdu \
        net-tools \
        nvtop \
        procps \
        python3-pip \
        python3-venv \
        ripgrep \
        strace \
        telnet \
        traceroute \
        tree \
        wget && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade \
    ipykernel \
    jupyterlab \
    jupyter-server-proxy \
    yq

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

USER ${USERNAME}
WORKDIR ${WORKSPACE}

EXPOSE 8888