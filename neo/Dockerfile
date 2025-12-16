FROM nvidia/cuda:12.8.1-base-ubuntu24.04 AS builder

# First build stage constructs /home/ubuntu
# Installs uv, webui, and builds full venv

# Install deps needed to compile venv
RUN apt-get update \
  && apt-get install -y \
    libcairo2-dev \
    gcc \
    g++ \
    curl

# Switch to ubuntu user for main setup
USER ubuntu
WORKDIR /home/ubuntu
ENV REFORGE_PATH=/home/ubuntu/stable-diffusion-webui
ENV UV_CACHE_DIR=${REFORGE_PATH}/venv/uvcache
ENV DEBIAN_FRONTEND="noninteractive"

# Version of python to install with uv
ENV UV_PYTHON=3.11

# Version variables controlled by https://github.com/snw35/dfupdate
ENV UV_VERSION=0.9.18
ENV UV_URL=https://github.com/astral-sh/uv/releases/download/${UV_VERSION}
ENV UV_FILENAME=uv-x86_64-unknown-linux-gnu.tar.gz
ENV UV_SHA256=c2def3db178ade63933fa15ffc96e882c196ce53e06173dcee05b36c5f6f68f5

# Install UV
RUN curl -L -O ${UV_URL}/${UV_FILENAME} \
  && echo "${UV_SHA256}  ./${UV_FILENAME}" | sha256sum -c - \
  && tar -xzf ./${UV_FILENAME} \
  && mkdir -p ./.local/bin \
  && mv ./uv-x86_64-unknown-linux-gnu/* ./.local/bin/ \
  && rm -rf ./uv-x86_64-unknown-linux-gnu ./${UV_FILENAME}

# Version variables controlled by https://github.com/snw35/dfupdate
ENV REFORGE_VERSION=2.7
ENV REFORGE_URL=https://github.com/Haoming02/sd-webui-forge-classic/archive/refs/tags/
ENV REFORGE_FILENAME=${REFORGE_VERSION}.tar.gz
ENV REFORGE_SHA256=3ba5c539f0535c2c5808d0bfc494ebe83940862c5a7b6a7f5a72301c18fab9be

# Install ReForge
RUN curl -L -O $REFORGE_URL/$REFORGE_FILENAME \
  && echo "$REFORGE_SHA256  ./${REFORGE_FILENAME}" | sha256sum -c - \
  && tar -xzf ./${REFORGE_FILENAME} \
  && mv sd-webui-forge-classic-${REFORGE_VERSION} stable-diffusion-webui \
  && rm -f ./${REFORGE_FILENAME} \
  && mkdir /home/ubuntu/config \
  && mkdir ${REFORGE_PATH}/output

COPY prepare_environment.py ${REFORGE_PATH}/prepare_environment.py
COPY entrypoint.sh ${REFORGE_PATH}/entrypoint.sh
COPY webui-user.sh ${REFORGE_PATH}/webui-user.sh
COPY webui.sh ${REFORGE_PATH}/webui.sh

# Copy entrypoint and set permissions as root
USER root
RUN chmod +x ${REFORGE_PATH}/entrypoint.sh \
  && chmod +x ${REFORGE_PATH}/webui-user.sh \
  && chmod +x ${REFORGE_PATH}/webui.sh \
  && chown -R ubuntu:ubuntu /home/ubuntu/
USER ubuntu

# Add both uv install dir and reforge install to path
ENV PATH="$PATH:${REFORGE_PATH}:/home/ubuntu/.local/bin"

# Version variables controlled by https://github.com/snw35/dfupdate
ENV SAGE_VERSION=2.2.0
ENV SAGE_URL=https://github.com/snw35/sageattention-wheel/releases/download/cu130-${SAGE_VERSION}/
ENV SAGE_FILENAME=sageattention-${SAGE_VERSION}-cp311-cp311-linux_x86_64.whl
ENV SAGE_SHA256=3ded16cde99ddc9c4f7e623e32aeb5f5ae815c0745f42828dce3579686319023

# Construct full venv
RUN curl -L -O ${SAGE_URL}/${SAGE_FILENAME} \
  && echo "$SAGE_SHA256  ./${SAGE_FILENAME}" | sha256sum -c - \
  && uv python install ${UV_PYTHON} --default \
  && uv venv ${REFORGE_PATH}/venv --seed --allow-existing \
  && . ${REFORGE_PATH}/venv/bin/activate \
  && uv pip install insightface \
  && uv pip install ninja \
  && uv pip install ./${SAGE_FILENAME} \
  && rm -f ./${SAGE_FILENAME} \
  && . ${REFORGE_PATH}/webui-user.sh \
  && python ${REFORGE_PATH}/prepare_environment.py \
  && pip cache purge \
  && uv cache clean


###############################################################################


FROM nvidia/cuda:12.8.1-base-ubuntu24.04

# Second stage copies homedir with webui install and pre-built venv
COPY --from=builder /home/ubuntu /home/ubuntu
ENV DEBIAN_FRONTEND="noninteractive"

# Runtime dependencies for WebUI
# Note that Pytorch JIT (just in time) compiliation requires gcc
RUN apt-get update \
  && apt-get install -y \
    bc \
    gcc \
    git \
    libgl1 \
    libglib2.0-0t64 \
    libtcmalloc-minimal4t64 \
    pciutils

USER ubuntu
WORKDIR /home/ubuntu
ENV REFORGE_PATH=/home/ubuntu/stable-diffusion-webui
ENV UV_CACHE_DIR=${REFORGE_PATH}/venv/uvcache
ENV UV_PYTHON=3.11
ENV PATH="$PATH:${REFORGE_PATH}:/home/ubuntu/.local/bin"

WORKDIR ${REFORGE_PATH}

EXPOSE 7860

# Mark named volume mounts
VOLUME /home/ubuntu/config
VOLUME /${REFORGE_PATH}/extensions

ENTRYPOINT ["entrypoint.sh"]

CMD ["webui.sh"]
