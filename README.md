# StreamWidgets
Display your follow/sub alerts or any other overlay directly on your game screen (does not work with games in full screen mode).

There are limitations:
 - I did not find the option which allows to activate the sounds without interaction (does not work suddenly),
 - Many video formats do not work (and there is no management of green funds).

To make this application work, you will need to install Python3 which you will find at this address: https://www.python.org/downloads/

Then you will have to install PyQt5 via the command prompt:
 - Download and unzip this project,
 - Use the keyboard shortcut WIN + R,
 - Write `cmd` then validate,
 - Write `cd` followed by a space, then drag the `StreamWidgets` folder into the command prompt and validate,
 - Finally copy the following command (right click on Windows to paste) and validate: `python -m pip install -r requirements.txt` (if that doesn't work, add `--user` to the command).

Now enter your personal information in the `config.json` file (for more details on the syntax, inquire about the JSON format):
 - screen: Default screen number to operate on,
 - duration: Time during which the yellow border remains displayed (sec),
 - default: List of widgets to display (numbers are percentages unless `px` is specified).
 - configs: Allows you to add overlay packs (these will be interchangeable).

Now that everything is installed, you can double-click on the `main.pyw` file, which will launch the application in your system tray.

__NOTE:__ The available options are to be found by right clicking on the application icon.
