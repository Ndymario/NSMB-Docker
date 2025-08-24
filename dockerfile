FROM ubuntu:24.04

# Prevent prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    cmake \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository ppa:ubuntu-toolchain-r/test -y && \
    apt-get update && apt-get install -y gcc-13 g++-13 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 100 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 100

# Install updates and curl/xz-utils
RUN apt-get update && apt-get install -y curl xz-utils && rm -rf /var/lib/apt/lists/*

# Download and install Arm GNU Toolchain 14.3
RUN curl -L -o /tmp/arm-toolchain.tar.xz \
    https://developer.arm.com/-/media/Files/downloads/gnu/14.3.rel1/binrel/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi.tar.xz && \
    tar -xJf /tmp/arm-toolchain.tar.xz -C /opt && \
    rm /tmp/arm-toolchain.tar.xz

# Add toolchain to PATH
ENV PATH="/opt/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi/bin:${PATH}"

# Install NDSpy
RUN pip install --break-system-packages ndspy

# Clone the latest NCPatcher and build it
RUN git clone https://github.com/TheGameratorT/NCPatcher.git /opt/NCPatcher && \
    mkdir /opt/NCPatcher/build && \
    cd /opt/NCPatcher/build && \
    cmake ../ -DCMAKE_BUILD_TYPE=Release && \
    make

# Add to PATH
ENV PATH="/opt/NCPatcher/build:${PATH}"

# Clone the latest NSMB Code Reference
RUN git clone https://github.com/MammaMiaTeam/NSMB-Code-Reference.git /opt/NSMB-Code-Reference/

# Copy scripts & NSMB-Docker NCPatcher configuration
RUN mkdir -p /app/scripts
COPY ./scripts/ /app/scripts
COPY ./arm9.json /app/
COPY ./buildrules.txt /app/
COPY ./ncpatcher.json /app/

# Set default working directory
WORKDIR /workspace

# Volume to store the converted SDK and a clean NSMB ROM for multi-project use
VOLUME /data

# Run the main Python script
CMD ["python3", "/app/scripts/nsmb.py"]