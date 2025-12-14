# ReForge

ReForge Stable Diffusion WebUI containers, updated weekly.

Currently builds:

 * ReForge Neo.

## Neo

[ReForge Neo Stable Diffusion WebUI](https://github.com/Haoming02/sd-webui-forge-classic) container with:

  * [`neo` branch from Haoming02.](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)
  * CUDA 12.8.
  * Sageattention 2.
  * Python 3.11 and UV.
  * Latest Torch and Torchvision.
  * Volumes and bind-mounts for all config, outputs, and runtime dependencies.
  * Everything included in the image.

### Tags

The following tags are available:

 * `snw35/reforge:neo` - Always points to the latest version of Neo.
 * `snw35/reforge:neo-x.x` - Points to a specific version of Neo.

### About

This container allows you to create AI images and videos with the latest models (Lumina, Quant, Wan, etc) on the most cutting-edge version of ReForge webui, with all the latest dependencies. You will need a host capable of running it (requirements outlined below). A modern gaming PC with an Nvidia GPU and Docker/Podman Desktop would be suitable without building something more serious (home server, etc).

This container is a **large image (around 8GB)** due to the WebUI's large number of dependencies. These are pre-packaged in the image, so nothing needs to be downloaded or compiled at runtime.

### Host Requirements

**Important - your host MUST have the CUDA runtime at 12 or above installed.** The CUDA version on the host must be equal to, or greater than, the version inside the container (12 in this case).

#### Hardware

* [An Nvidia GPU with 8GB+ VRAM and CUDA 12 support, RTX 20+ recommended.](https://developer.nvidia.com/cuda-gpus)
* At least 16GB of RAM for SD/XL and distilled models, 64GB for full versions of models (e.g Flux).
* At least 200GB of disk space for dependencies and models (500GB or more recommended).
* Using a VM is fine, as long as your GPU is passed-through and detected inside it.

#### Operating System (OS) Install Options

You need a container runtime that can support passing your GPU through to the container:

 * Windows: [Install CUDA 12 or 13](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/), then either [Docker Desktop with GPU pass-through](https://docs.docker.com/desktop/features/gpu/) or [Podman Desktop with GPU pass-through.](https://podman-desktop.io/docs/podman/gpu)
 * MacOS: [Install CUDA 12 or 13](https://developer.nvidia.com/nvidia-cuda-toolkit-developer-tools-mac-hosts), then [Podman Desktop with GPU pass-through.](https://podman-desktop.io/docs/podman/gpu)
 * Linux: [Install CUDA 12 or 13](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html), then [Podman Desktop with GPU pass-through.](https://podman-desktop.io/docs/podman/gpu)
 * Virtual Machine: A Linux VM with GPU pass-through works well (see below).

#### Installing on a VM or native Linux:

If you go the Virtual Machine route, or want to set up natively on Linux, you will need to install:

 * [CUDA 12 or 13 Runtime.](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
 * [A supported Linux distro for CUDA 12 or 13 (Ubuntu server 24.04 LTS recommended).](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#system-requirements)
 * [Compatible Nvidia drivers (both 'open' and 'proprietary' flavours work).](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/index.html)
 * [Docker-CE.](https://docs.docker.com/engine/install/)
 * [Nvidia container toolkit.](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

Once you have all of the above installed and working, you can test this image in standalone mode to see if it will run:

`docker run -it --runtime=nvidia --gpus all -p 7860:7860 snw35/reforge:neo`

The webui should be available on port 7860 of the VM/host once it has started up, e.g `http://your-host-ip:7860`

Any errors that cause the container to exit, or to display CUDA/Nvidia runtime or driver errors will likely be fatal and need troubleshooting on the host to resolve.

### Running Long-Term

For long-term use the bundled `docker-compose.yaml` file is required because it maps critical files (such as output images and configuration) to named volumes and the local directory, preserving them between restarts.

The purpose of each named volume is explained below:

 * `reforge-config` - Webui settings files.
 * `reforge-extensions` - Any custom extensions installed by the user.

Clone the repo and start the compose project:

```
git clone https://github.com/snw35/reforge
docker compose up -d && docker compose logs -f
```

This will create two important directories:

 * `outputs` <- **This is where your generated images are placed**.
 * `models` - Place your models, Loras, etc here.

### Downloading Models

See Haoming02's [wiki page for where to download model files](https://github.com/Haoming02/sd-webui-forge-classic/wiki/Download-Models), and for [references on how to run them](https://github.com/Haoming02/sd-webui-forge-classic/wiki/Inference-References).

Place your model files in the `models` folder [in this linked layout.](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo/models) You will need to create the sub-folders for each type of model. This is bind-mounted into the container so all files are available to the webui.

 * Put Checkpoint / UNet / DiT in models/Stable-diffusion.
 * Put Text Encoders in /models/text_encoder.
 * Put VAE in /models/VAE.

 ### Building

 This container can be built by simply cloning the repo and running e.g `docker build -t reforge:neo ./neo/`.

 The build is two-stage due to the compilers and dev packages needed to compile the venv. A fair number of dependencies are 'sdist', e.g source distributions that require compilation on install. These packages are not needed for runtime, so can be dropped and left behind in the 'builder' image.

 Everything is packaged inside `/home/ubuntu`, including all runtime files and the WebUI install. The `ubuntu` user is used to run the WebUI itself. The CUDA `-base-` image is used as the base image, because the CUDA runtime libraries are required.

### Other CUDA Versions / Older Hardware

This repo will not provide containers or support for older CUDA versions (e.g 11.x, needed by some old Nvidia hardware) at the current time, as this project is focused on achieving the fastest performance on the the latest versions of ReForge and dependencies. The area of A.I image generation is fast moving and installation methods can vary widely between e.g CUDA 11.x and CUDA 12 for the same packages.
