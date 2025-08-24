# NSMB Docker
A simple all-in-one solution for setting up the [NSMB Code Mod Template](https://github.com/MammaMiaTeam/NSMB-Code-Template).

## Requirements
- [Docker](https://docs.docker.com/desktop/)
- A copy of New Super Mario Bros. (USA region)
- NitroSDK v3.0
- Nitro System

## How-to Use
1. Create a folder named `include` in this project directory
2. Create a folder named `nitrofs` and insert the `banner.bin` from your ROM. (Or you may use a custom one)
3. Copy the contents of the include folder from the NitroSDK into your new include folder
4. Copy the contents of the include folder from Nitro System into your new include folder
5. Rename your ROM to `nsmb.nds`
6. [TODO: Update with step to pull the image from GitHub]
7. Run the container using `docker run -v ./source:/app/source -v ./nitrofs:/app/nitrofs -v "$PWD:/workspace" -v nsmb-data:/data nsmb`

## Other Info
- Placing files inside of your `nitrofs` folder will have them appended in the ROM. For example, `nitrofs/root/foo/bar` will add a folder named `foo` containing a file named `bar` into the ROM.
> Replacing files in the ROM coming in a future version!

## Advanced Usage
Some paths that might be helpful if you decide to mess around with the files are:
- `/workpace/`: This is your project mounted via a volume (defined by `-v $PWD:/workspace`)
- `/app/`: This is the working environment for NCPatcher and the other scripts 
- `/data/`: This is the persistant data volume created by `-v nsmb-data:/data` and used by `nsmb.py`.
    - `/data/include/`: Sub-directory that contains the NitroSDK and Nitro System. `nsmb.py` runs the `convert_sdk.py` script on these files for you.
    - `/data/nsmb.nds`: This is a copy of your clean ROM used by `nsmb.py`.
- `/opt/`: This is the directory in the image that tools are cloned to
    - `/opt/NCPatcher/`: Sub-directory for NCPatcher. The built executable is added to the `PATH` by the Dockerfile (`/opt/NCPatcher/build`).
    - `/opt/NSMB-Code-Reference/`: Sub-directory for the NSMB-Code-Template.

Some examples of what you could customize:
- Use a specific version of the code reference by adding `-v ./My-Code-Reference:/opt/NSMB-Code-Reference` to the `docker run` command (where `My-Code-Reference` is a folder containing a modified code refernce)
- Split your workspace into sub-projects and use the `arm9.json` 

### Credits
Shoutout to [@TheGameratorT](https://github.com/TheGameratorT) for the insert code/files python scripts and for creating [NCPatcher](https://github.com/TheGameratorT/NCPatcher/).

This repo is based off of the [NSMB Coding Template](https://github.com/MammaMiaTeam/NSMB-Code-Template).