ARG IMAGE_NAME=nvcr.io/nvidia/tritonserver:25.05-vllm-python-py3
FROM ${IMAGE_NAME}
LABEL maintainer="ninja-con-gafas <el.ninja.con.gafas@gmail.com>"

ARG DEV=false
ARG UID=1001
ARG GID=1001
ARG USERNAME=ai-lab
ARG WORKSPACE=/home/ai-lab/workspace

ENV DEBIAN_FRONTEND=noninteractive
ENV DEV=${DEV}
ENV PATH="/opt/llama.cpp/full:/opt/llama.cpp/build/bin:${PATH}"

RUN groupadd -g ${GID} ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME} && \
    mkdir -p ${WORKSPACE} && \
    chown -R ${UID}:${GID} ${WORKSPACE}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        curl \
        git \
        libcurl4-openssl-dev \
        libgomp1 \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*
    
RUN git clone --depth=1 https://github.com/ggerganov/llama.cpp.git /opt/llama.cpp && \
    cd /opt/llama.cpp && \
    cmake -B build \
        -DGGML_NATIVE=OFF \
        -DGGML_CUDA=ON \
        -DGGML_BACKEND_DL=ON \
        -DGGML_CPU_ALL_VARIANTS=ON \
        -DLLAMA_BUILD_TESTS=OFF \
        -DCMAKE_EXE_LINKER_FLAGS=-Wl,--allow-shlib-undefined . && \
    cmake --build build --config Release -j$(nproc) && \
    mkdir -p /opt/llama.cpp/lib && \
    find build -name "*.so" -exec cp {} /opt/llama.cpp/lib \; && \
    mkdir -p /opt/llama.cpp/full && \
    cp build/bin/* /opt/llama.cpp/full && \
    cp *.py /opt/llama.cpp/full && \
    cp -r gguf-py /opt/llama.cpp/full && \
    cp -r requirements /opt/llama.cpp/full && \
    cp requirements.txt /opt/llama.cpp/full && \
    cd /opt/llama.cpp && pip install -e . && \
    rm -rf build

RUN if [ "$DEV" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            dnsutils \
            findutils \
            htop \
            iotop \
            iproute2 \
            iputils-ping \
            jq \
            less \
            lsof \
            nano \
            ncdu \
            net-tools \
            nvtop \
            procps \
            ripgrep \
            strace \
            telnet \
            traceroute \
            tree \
            wget \
            yq && \
        rm -rf /var/lib/apt/lists/* && \
        python3 -m pip install --no-cache-dir \
            ipykernel \
            jupyter-server-proxy \
            jupyterlab; \
    fi

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

USER ${USERNAME}
WORKDIR ${WORKSPACE}

EXPOSE 8000 8001 8002 8080 8888