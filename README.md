Steam .acf AutoUpdateBehavior Modifier Script

Version: 1.0.0

Date: 2025-11-02

Author: Some anonymous wannabe coder who leaned on ChatGPT to do most of the coding for this. But it works.

Permissions: I can hardly take credit for this. I suck at coding. Do whatever you like with it. 
Pretend that you coded it for all I care. Go nuts.

Description:

For some time now, the default update behavior for Steam games has been "Let Steam Decide" 
when to update. This results in Steam scheduling any updates for games for some 
(seemingly random) point in the future, from hours to even several days.
Many have claimed that this change was made during the COVID 19 pandemic to stagger when users' 
computers downloaded updates to reduce network congestion.

Unfortunately, this means sometimes when you go to play a game, you will find that it has been 
updated by the developers, but rather than immediately downloading the update, Steam has scheduled 
the download for some time in the future, so you need to manually tell Steam to download the update 
and then wait (sometimes for a very long time, depending on the size of the update) before the game 
is ready to play. As a user, you DO have the ability to set each game to automatically download updates 
as soon as they are ready, but you have to do this manually for each and every game. There is no way to 
set games to immediately download globally. If you have hundreds of games installed, this can get 
extremely tedious, and you still need to remember to change the setting for each new game you install.

This app changes that. From the top down, this app is written to quickly and seamlessly set every one of 
your Steam games to automatically download updates as soon as they are available. It is written in such 
a way that it requires no interaction from the user after running, meaning that it can be set to run 
automatically once a day without any intervention from you. Set it and forget it.

In a nutshell, this is what it does:

- When first run, it automatically scans each of your hard drives for a "steamapps" folder. It does this
  very quickly due to some simple heuristics built into the program (it scans for a "steamapps" folder
  under a "Steam" folder and searches for the "Steam" folder using a few priority and common directory
  names such as "Program Files (x86)", "Steam" and "Games".

- It will usually find all instances of steamapps directories across your system. It will then create a
- config.txt file containing these detected directories as well as other settings that can be modified:

Backup files before they are changed (Default on)
Log files (Default on)
Log file retention (Default 3)
Custom strings to be searched and replaced (Already set - should not be changed unless necessary, this 
is just future proofing in case Valve changes how flags are displayed and handled in files.)

If no steamapps directories are detected, the user will receive an error message and the directory paths 
can be added to the config.txt file under the comment calling for them (One per line)

- Once this is complete, the program will automatically search for all of the appmanifest_xxxxxx (.acf)
  files (one of these is automatically created by Steam every time you install a game, and this is where
  the Steam settings for that game are stored) in the detected directories or directories manually set
  in the config.txt file. It will then back all of them up before performing any modifications. After this,
  it will replace the string that specifies that steam should decide when to update the game with the string
  to specify that the game should automatically update as soon as an update is available. That is all.
  It's very simple.
  
- After it has done this, the app will output the filenames (and the corresponding names of the games) that
  it has modified. It will then save all of its output to a log file so that you can review any of its operations.

That's it.

Note: For best results, quit Steam completely before running this script. While the script will still
sucessfully make the necessary changes, Steam will have trouble recognising these changes if they
are made while it is running.

Disclaimer: You should backup all of your ACF files manually before running this, even though it does so for you. 
It really shouldn't cause any problems with them, but a disclaimer is a disclaimer. Just do your due diligence.

Features:
    - Search and replace specific values in Steam .acf files. (configurable)
    - Option to back up the .acf files before modification. (togglable)
    - Automatic detection of Steam installation directories.
    - Log file creation for tracking script execution. (togglable)
    - Keeps only a specified number of most recent log files. (configurable)

Requirements:
    - Python 3.x
    - Python modules: os, sys, shutil, re, subprocess
    - Dependency check at runtime with routine to acquire uninstalled modules

Usage:
    
    1. Place the script in a directory.
    
    2. Make sure Steam is not running for best results. (See above)
    
    3. Run the script. (You can do this through a terminal or by downloading the 
    optional Run.bat batch file and copying it to the same directory as the main file
    and running the batch file.) It will either find or create a configuration file 
    (config.txt) and automatically scan for Steam's installation directories.
    
    4. It will modify the "AutoUpdateBehavior" setting in the relevant .acf files.
    
    5. Optionally, you can enable backups for all the .acf files.

Notes:
    - The script will automatically back up the files if the 'backup_enabled'
      option is set to true in config.txt. (default true)
    - Logs are stored in a 'logs' directory and older logs are cleaned up
      based on the 'max_log_files' configuration. (dafault on, max. 3 logs)
