
# Harbor-Stream-Labels
A basic HTTP Client written in Python to create and update resources that can be used to display statistics for the MCC Island Minecraft server on an OBS scene.

## What is this project for?

I created the concept for HarborSL when I wanted a way to display some of my statistics on my livestreams.  
The program (at `v0.0.4-beta` and earlier) was created in 11 days as a summer assignment to create 'a utility software or game'. I think I may have done much more than was expected but it was good motivation to create this project eventually and it was the only idea I had. 

## How to use?

*HarborSL is in a beta state so only source code is available.*  
*Unknown errors may occur.*  
*If you have API disabled for you account on MCCI or have not logged on to the server before, the program will not work as this case is not yet accounted for.*

- You must have Python (at least 3.14.0) installed on you machine.  
This can be downloaded from the [Python Website](https://www.python.org/downloads/).
- The following modules must be imported to Python globally or into a [Virual Environment](https://docs.python.org/3/library/venv.html).  
*[Guide for installing modules](https://docs.python.org/3/installing/index.html)*
  - Requests `pip install requests`
  - PyYaml `pip install pyyaml`
- Head to the releases page and download `source.zip` from the latest release / pre-release.
- Extract in the desired location.
- Rename the folder `resources.template` in the `src` folder to `resources`.
- Now open `config.yml` from `resources`. (If you can't open this file, rename it to `config.txt` while you edit, and rename it back to `config.yml` once you have saved it)
- Change the `user` field to your minecraft username. (This field is case insensitive so don't worry about getting capitalisation correct)
- Now head to the [Noxcrew Gateway](https://gateway.noxcrew.com/). You can log in to generate an API key. Copy and past this into the `API-Key` field.
- For now, leave the other fields alone and save the file.
- Now you can run the Python file.
  - This can be done either by double clicking `HarborSL.py` or opening the terminal and changing the working directory to the `src` directory and run the command `python HarborSL.py` (or `python3 HarborSL.py`)
  - You may run this file any other way but ensure the working directory is set to `~/src`
- If the program ran successfully, the last line in the terminal should be `[Thread] Updated label content.`. This may take a few seconds to show up. Now close the terminal window
- Now check the `resources` folder. It should contain the new `labels` folder.  
This contains text and image files which can be loaded into OBS to design custom stats overlays for streaming.
- These files will not contain your statistics yet.
- Re-open `config.yml` and look at the `getData` section. Change the `overallData` field to `true`.  
You can do this for the other 3 fields later.
- Once again, save `config.yml` and run the Python program as you did before. Once `[Thread] Updated label content.` shows, close the terminal again.
- Now check `~/src/resources/labels/txt/crownLevel/overall/level.txt`. This should include your current crown level.
- If all above has worked you can now use the program freely. Bear in mind this should be for testing purposes, not serious use.

### What next?

- Perhaps enabled other statistics by changing their value in the config file to `true`.
- To disable a stat, set its value back to `false`.
- The main requesting mechanism loops every set number of minutes so you can keep the terminal open while you play/test.
- The number of minutes can be configured by the `resetTime` field in the config file.  
This field has a min value of 4 and a max value of 45. The recommended and default time is 15 to avoid ratelimiting.
