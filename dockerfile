FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    cmake \
    build-essential \
    sudo \
    curl \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Use BuildKit-provided TARGETARCH (amd64 or arm64)
ARG TARGETARCH

# Map TARGETARCH → ARCH (x86_64 / aarch64) for toolchain download
RUN if [ "$TARGETARCH" = "amd64" ]; then ARCH=x86_64; \
    elif [ "$TARGETARCH" = "arm64" ]; then ARCH=aarch64; \
    else echo "Unsupported TARGETARCH=$TARGETARCH" && exit 1; fi && \
    curl -L -o /tmp/arm-toolchain.tar.xz \
      "https://developer.arm.com/-/media/Files/downloads/gnu/14.3.rel1/binrel/arm-gnu-toolchain-14.3.rel1-${ARCH}-arm-none-eabi.tar.xz" && \
    tar -xJf /tmp/arm-toolchain.tar.xz -C /opt && \
    rm /tmp/arm-toolchain.tar.xz

# Add toolchain to PATH
ENV PATH="/opt/arm-gnu-toolchain-14.3.rel1-*/bin:${PATH}"

# Install NDSpy
RUN pip install --break-system-packages ndspy

# Clone the NCPatcher repo and build NCPatcher
ARG NCPATCHER_TAG=""
# Clone the repo and checkout specified tag or latest
RUN git clone https://github.com/TheGameratorT/NCPatcher.git /opt/NCPatcher && \
    cd /opt/NCPatcher && \
    if [ -z "$NCPATCHER_TAG" ]; then \
        git fetch --tags && \
        LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`) && \
        git checkout "$LATEST_TAG"; \
    else \
        git checkout "$NCPATCHER_TAG"; \
    fi && \
    mkdir build && cd build && \
    cmake ../ -DCMAKE_BUILD_TYPE=Release && \
    make

ENV PATH="/opt/NCPatcher/build:${PATH}"

# Clone the latest NSMB Code Reference
ARG CODE_TEMPLATE_COMMIT=""
RUN if [ -n "$CODE_TEMPLATE_COMMIT" ]; then \
      git clone https://github.com/MammaMiaTeam/NSMB-Code-Reference.git /opt/NSMB-Code-Reference && \
      cd /opt/NSMB-Code-Reference && \
      git checkout "$CODE_TEMPLATE_COMMIT"; \
    else \
      git clone https://github.com/MammaMiaTeam/NSMB-Code-Reference.git /opt/NSMB-Code-Reference/; \
    fi

# Copy scripts & NSMB-Docker NCPatcher configuration
RUN mkdir -p /app/scripts
COPY ./scripts/ /app/scripts
COPY ./arm9.json /app/
COPY ./ncpatcher.json /app/

# Create the build folder
RUN mkdir /app/build

# Set default working directory
WORKDIR /app

# Volume to store the converted SDK and a clean NSMB ROM for multi-project use
VOLUME /data

# Run the main Python script
CMD ["python3", "/app/scripts/nsmb.py"]
