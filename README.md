# NSMB Docker
A simple all-in-one solution for setting up the [NSMB Code Mod Template](https://github.com/MammaMiaTeam/NSMB-Code-Template).

## Requirements
- [Docker](https://docs.docker.com/desktop/)
- A copy of New Super Mario Bros. (USA region ROM)
- NitroSDK v3.0
- Nitro System

## How-to Use
1. Create a folder named `include` in the root of your project.
2. Create a folder named `nitrofs` and insert the `banner.bin` from your ROM. (Or you may use a custom one)
3. Copy the contents of the include folder from the NitroSDK into your new include folder
4. Copy the contents of the include folder from Nitro System into your new include folder
5. Place your ROM of NSMB into the root of your project.
6. Rename your ROM to `nsmb.nds`
7. [TODO: Update with step to pull the image from GitHub]
8. Run the container using `docker run -v ./source:/app/source -v ./nitrofs:/app/nitrofs -v "$PWD:/workspace" -v nsmb-data:/data nsmb`

## Other Info
- Placing files inside of your `nitrofs` folder will have them appended in the ROM. For example, `nitrofs/foo/bar` will add a folder named `foo` containing a file named `bar` into the ROM.
> Replacing files in the ROM coming in a future version!

## Advanced Usage
### Build Flags
By default, the image that is published fetches the latest NCPatcher (by tag) and latest NSMB Code Reference (by commit hash). I have created various build flags for specifying a specific release to use.

- `ARCH`: `x86_64` or `aarch64` for what architecture of the ARM toolchain should be downloaded to the image.
- `NCPATCHER_TAG`: specifies what release tag NCPatcher should be cloned from (default is latest)
- `CODE_TEMPLATE_COMMIT`: specifies what commit hash that the code template will be at (default is latest)

For example, if you wanted to use `v1.0.9` of NCPatcher with the NSMB Code Reference at commit `b4e7950` with `aarch64`, your build command would look like:
```
docker build --build-arg ARCH=aarch64 --build-arg NCPATCHER_TAG=v1.0.9 --build-arg CODE_TEMPLATE_COMMIT=b4e7950 . -t nsmb
```

### File Paths
Some paths that might be helpful if you decide to mess around with the files:
- `/workpace/`: This is your project workspace mounted to the image (defined by `-v $PWD:/workspace`).
- `/app/`: This is the working environment for NCPatcher and the other scripts.
    - `/app/scripts/`: Sub-directory that contains the various scripts (`scripts` folder in this repo) used by NSMB-Docker.
    - `/app/arm9.json`: The default `arm9.json` configured for NSMB-Docker.
    - `/app/ncpatcher.json`: The default `ncpatcher.json` configured for NSMB-Docker.
- `/data/`: This is the persistant data volume created by `-v nsmb-data:/data` and used by `nsmb.py`.
    - `/data/include/`: Sub-directory that contains the NitroSDK and Nitro System. `nsmb.py` runs the `convert_sdk.py` script on these files for you.
    - `/data/nsmb.nds`: This is a copy of your clean ROM used by `nsmb.py`.
- `/opt/`: This is the directory in the image that tools are cloned to
    - `/opt/NCPatcher/`: Sub-directory for NCPatcher. The built executable is added to the `PATH` by the Dockerfile (`/opt/NCPatcher/build`).
    - `/opt/NSMB-Code-Reference/`: Sub-directory for the NSMB-Code-Template.

Some examples of what you could customize:
- Use a locally modified version of the code reference by adding `-v ./My-Code-Reference:/opt/NSMB-Code-Reference` to the `docker run` command (where `My-Code-Reference` is a folder containing a modified code refernce)
- Modify `ncpatcher.json` to add more include folders. `-v ./ncpatcher:/app/ncpatcher.json` would replace `ncpatcher.json` with the `ncpatcher.json` in the `PWD`.

### Credits
Shoutout to [@TheGameratorT](https://github.com/TheGameratorT) for the insert code/files python scripts and for creating [NCPatcher](https://github.com/TheGameratorT/NCPatcher/).

This repo is based off of the [NSMB Coding Template](https://github.com/MammaMiaTeam/NSMB-Code-Template).