FROM nvidia/cuda:13.1.1-base-ubuntu24.04 AS builder

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

# Version variables controlled by https://github.com/snw35/dfupdate
ENV UV_VERSION=0.10.3
ENV UV_URL=https://github.com/astral-sh/uv/releases/download/${UV_VERSION}
ENV UV_FILENAME=uv-x86_64-unknown-linux-gnu.tar.gz
ENV UV_SHA256=c60b9956a0e6727f0ddd881c303a706c6408b2047f3a8fa4d1454a826338ccdc

# Install UV
RUN curl -L -O ${UV_URL}/${UV_FILENAME} \
  && echo "${UV_SHA256}  ./${UV_FILENAME}" | sha256sum -c - \
  && tar -xzf ./${UV_FILENAME} \
  && mkdir -p ./.local/bin \
  && mv ./uv-x86_64-unknown-linux-gnu/* ./.local/bin/ \
  && rm -rf ./uv-x86_64-unknown-linux-gnu ./${UV_FILENAME}

# Version variables controlled by https://github.com/snw35/dfupdate
ENV REFORGE_VERSION=2.13
ENV REFORGE_URL=https://github.com/Haoming02/sd-webui-forge-classic/archive/refs/tags/
ENV REFORGE_FILENAME=${REFORGE_VERSION}.tar.gz
ENV REFORGE_SHA256=0eb8eebc09d76c1749919e636623939d45c2a273a00ad53430636a03dc9b8dc6

# Install ReForge
RUN curl -L -O $REFORGE_URL/$REFORGE_FILENAME \
  && echo "$REFORGE_SHA256  ./${REFORGE_FILENAME}" | sha256sum -c - \
  && tar -xzf ./${REFORGE_FILENAME} \
  && mv sd-webui-forge-classic-${REFORGE_VERSION} stable-diffusion-webui \
  && rm -f ./${REFORGE_FILENAME} \
  && mkdir /home/ubuntu/config \
  && mkdir ${REFORGE_PATH}/output

COPY prepare_environment.py ${REFORGE_PATH}/prepare_environment.py
COPY get_python_version.py ${REFORGE_PATH}/get_python_version.py
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
# Stop sage from automatically updating due to python version being unknown at build time
ENV SAGE_VERSION=2.2.0
ENV SAGE_URL=https://github.com/snw35/sageattention-wheel/releases/download/cu12-${SAGE_VERSION}-cu13-${SAGE_VERSION}/
ENV SAGE_SHA256=599bede74bb0be04157b24939f02ea0e741d2e9a4e20abc6ae7c98a00c31f4ce

# # Construct full venv
RUN export PYTHON_VERSION=$(python3 ${REFORGE_PATH}/get_python_version.py) \
  && export SAGE_CP=$(python3 ${REFORGE_PATH}/get_python_version.py -strip) \
  && export SAGE_FILENAME=sageattention-${SAGE_VERSION}+cu13-cp${SAGE_CP}-cp${SAGE_CP}-linux_x86_64.whl \
  && curl -L -O ${SAGE_URL}/${SAGE_FILENAME} \
  && uv python install $PYTHON_VERSION --default \
  && uv venv ${REFORGE_PATH}/venv --clear --seed --allow-existing \
  && . ${REFORGE_PATH}/venv/bin/activate \
  && uv pip install insightface \
  && uv pip install ninja \
  && uv pip install openai-clip \
  && uv pip install ./${SAGE_FILENAME} \
  && rm -f ./${SAGE_FILENAME} \
  && . ${REFORGE_PATH}/webui-user.sh \
  && python ${REFORGE_PATH}/prepare_environment.py \
  && pip cache purge \
  && uv cache clean


###############################################################################


FROM nvidia/cuda:13.1.1-base-ubuntu24.04

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
ENV PATH="$PATH:${REFORGE_PATH}:/home/ubuntu/.local/bin"

WORKDIR ${REFORGE_PATH}

EXPOSE 7860

# Mark named volume mounts
VOLUME /home/ubuntu/config
VOLUME /${REFORGE_PATH}/extensions

ENTRYPOINT ["entrypoint.sh"]

CMD ["webui.sh"]
