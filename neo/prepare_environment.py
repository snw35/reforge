from modules import launch_utils

args = launch_utils.args

# Simple script to launch webui's prepare_environment() function.
# This is needed to install all out-of-band dependencies that are not declared elesewhere,
# and is needed to build a full, complete venv before runime.

prepare_environment = launch_utils.prepare_environment

def main():
    # We set this flag to allow buidling on non-GPU runners
    args.skip_torch_cuda_test = True
    prepare_environment()

if __name__ == "__main__":
    main()
