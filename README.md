# NSMB Docker
A simple all-in-one solution for setting up the [NSMB Code Mod Template](https://github.com/MammaMiaTeam/NSMB-Code-Template).

## Requirements
- [Docker](https://docs.docker.com/desktop/)
- A copy of New Super Mario Bros. (USA region)
- NitroSDK v3.0
- Nitro System

## How-to
1. Create a folder named `include` in this project directory
2. Create a folder named `nitrofs` and insert the `banner.bin` from your ROM. (Or you may use a custom one)
3. Copy the contents of the include folder from the NitroSDK into the new include folder
4. Copy the contents of the include folder from Nitro System into the new include folder
5. Rename your ROM to `nsmb.nds`
6. Build the container using `docker build -t nsmb .`
>Note: on Apple Silicon, use this instead `docker buildx build --platform linux/amd64 -t nsmb-amd64 .`
7. Run the container using `docker run -v "$PWD:/workspace" -v nsmb-data:/data nsmb `
>Note: on Apple Silicon, use this instead `docker run --platform linux/amd64 -v "$PWD:/workspace" -v nsmb-data:/data nsmb-amd64`

## Other Info
- Placing files inside of your `nitrofs` folder will have them appended in the ROM. For example, `nitrofs/root/foo/bar` will add a files named `bar` into the ROM.

## Advanced Usage
The script will try to use the `arm9.json`, `buildrules.txt`, and `ncpatcher.json` located inside of the current workspace. You may modify the `NSMB-Docker` versions of these files if you would like maximum control over the build process.


### Credits
Shoutout to [@TheGameratorT](https://github.com/TheGameratorT) for the insert code/files python scripts and for creating [NCPatcher](https://github.com/TheGameratorT/NCPatcher/).

This repo is based off of the [NSMB Coding Template](https://github.com/MammaMiaTeam/NSMB-Code-Template).