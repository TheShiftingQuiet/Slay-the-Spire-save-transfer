# Introduction

This project lets you move your current Slay the Spire run's save, your run history and your statistics/unlocks/etc from your PC to your android phone and vice-versa, using USB connection and ADB.  
  
You ***shouldn't*** need a rooted phone - this script works for me on my non-rooted android phone. Your mileage may vary - hopefully it won't.  

You need the following prerequisites:  
1. You must own **Slay the Spire** on both PC (tested with a Steam copy) and Android (tested with a Play Market copy)  
2. You must have **Python 3.9** or above installed (make sure it's in your PATH environment variable) on PC.  
3. You need an android phone with USB debugging enabled, and its USB cable (which you can connect to your computer that has Slay the Spire). Enabling USB debugging doesn't require rooting your phone in most cases, so you should be able to turn it on for running this script.  
4. You need the **Android Debug Bridge** (`adb`) executable in your PATH environment variable on PC.  
   You can find guides on how to set it up online, but in short, for Windows, you normally need to download the [Android SDK Platform Tools ZIP file for Windows.](https://dl.google.com/android/repository/platform-tools-latest-windows.zip), then extract it to some folder and add that folder to the PATH environment variable.  
5. If you've done everything right, you should be able to run the command `adb version` in your command prompt (hit Win+R, type "cmd", press "Open") and see the version of `adb`. You should also be able to run `python --version` and see the version of python (must be at least 3.9).  
  
> **Note**:  
> The synchronization is **not continuous**. This means that it does not automatically keep your data in sync across your PC and android phone, this is just a tool to move from PC to phone and vice-versa. Each time you transfer data, you are basically replacing the Slay the Spire data on one device with the data from the other.  
>  
> For example, If you make progress on your PC and then transfer outdated data from your Android phone back to your PC, you could lose your PC progress. While your run history for the new runs will not be lost, you will most likely lose your progression, unlocks, and the current run save ("lose" as in, they'll revert to how they are on your phone).  
>   
> Thus, it's important to be careful when choosing whether to transfer data from your PC to your Android device or vice versa.  
>   
> I also strongly recommend you make backups of the three folders (`preferences`, `runs`, `saves`) so that you always have something to roll back onto (or even before/after every transfer, if you want to be that careful). This is not done automatically, not at the moment at least.  
  
# FAQ  
1. **Does this transfer [i]everything[/i], or are there things it doesn't transfer?**  

   I believe it transfers pretty much everything (excluding things like settings, input mappings etc which wouldn't even make sense to transfer between different devices). It transfers your run history (which most people struggled with - either ending up with non-working timestamps or straight up crashing their game, but I found the solution for it), it transfers your statistics and unlocks (which is pretty straightforward), and it transfers your active save file as well for any ongoing runs (which many people have already figured out how to do, credit for the current active run save "decryption" method goes to them. I would credit by name but I forgot where I first saw that the XOR key was "key"). If you notice anything relevant it doesn't transfer, feel free to let me know.  
   
2. **Will I get the achievements on Steam from progress I made on mobile when I transfer my data?**  
   
   Surprisingly, yes! From my testing, if you play on mobile and, say, beat a boss without taking damage, get 9 energy in a single turn, beat the game as Silent, etc, and then you transfer your saves to PC - as soon as you launch the game, you will get all of the corresponding achievements for that! 
   
   My assumption is that the game checks your runs history on launch and distributes achievements based on that, so you should be able to get most (if not all) of the achievements this way, by playing the game on mobile and just transfering your runs to your PC to unlock the correct achievements on Steam.  

3. **Is this safe?**  

   Yes, everything happens in one script - the '.py' file. It's written in plain python, using only standard libraries, and everything is laid out plainly for you to look over to ensure things look right. The script also doesn't delete anything it didn't create automatically, it only performs copy with replacement in both directions. Backups are still recommended as you could accidentally replace newer saves with older ones if you do the wrong direction.  

4. **Can I get banned for this?**  

   I highly doubt that, considering you legally own both copies, and that the developers seem supportive of it. They've mentioned you can transfer saves manually in one of the threads I've seen, and the system that lets you unlock achievements based on just your run history seems to indicate they support it, as well!  
   
5. **Do I need to run this every time I want my progress to be transferred, or is it synced automatically?**  
  
   It's not synced automatically - you need to follow the transfer steps each time you want to sync between your PC and phone. Read more in a note above.
  
6. **Can you bundle this into an executable so that I don't need to install Python and 'adb'?**  
  
   I'd rather not - I don't like the idea of sharing unsigned executables and assuming responsibility, especially since someone might just tamper with it and reupload it. With pure python code, everything is transparent - installing Python and downloading 'adb' is pretty straightforward.
   
7. **Does this work with iOS or is it only for Android?**  
  
   The script doesn't work on iOS, unfortunately - it uses 'adb' which is specific to android. You can follow the manual guide or modify the script to work with iOS if you have experience with iOS and know how to move files to it from PC - I don't own an iPhone so I haven't a clue.  
  
8. **Does this work on MacOS/Linux, or just Windows?**  
  
   I've only tested on Windows, but it should in theory work across all platforms. No guarantees though, if something breaks it should be relatively simple to fix though.  

9. **Does this support mods?**  
   
   I haven't tested it with any. Simple mods that don't store any extra data should probably be fine, and gameplay mods that store their data in the existing, defined structure, with no breaking differences between the two platforms *might* work fine - but then again, the mobile version could just crash when encountering data it doesn't recognize.  

# Configuration

Here's a sample configuration file. You can find it in `config.ini`.  
  
```ini
[DEFAULT]
; This is the path to the root directory of your slay the spire game on PC. 
; You can find it by right-clicking on Slay the Spire on steam -> Properties -> Installed Files -> Browse.
; Simply copy the path to that folder down below. It should contain folders like "runs", "saves", "preferences", or files like SlayTheSpire.exe.
PcPathToGame = C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire\

; This is the path to the root directory of your slay the spire game on android.
; It should be the same for most people who downloaded it from the Play Market, so try to leave it as the default.
; At most you might need to change the /sdcard/ to something else, but you likely won't need to.
AndroidPathToGame = /sdcard/Android/data/com.humble.SlayTheSpire/

; For some reason, the mobile version stores timestamps in GMT, while the PC version stores it in your local timezone.
; To prevent mistmatches, please enter the offset for your timezone, in hours (and optionally minutes).
; For example, if you're EST (Eastern Standard Time - no daylight savings) - that's GMT-5, which is 5 hours behind GMT. You'd put -5 for that.
; Or, if you're GMT (Greenwich Mean Time), just put 0
; Or, if you're NPT (Nepal Standard Time), that's GMT+5:45, in other words 5 hours and 45 minutes ahead, in which case you'd put +5:45
LocalTimezoneOffsetHours = +4
```
  
# Syncing from PC to mobile  
  
1. Check the `config.ini` file in the root directory of this project. Make sure to change the config parameters if they don't apply in your case.  
2. Make sure to enable USB debugging on your phone  
3. Connect via USB to PC  
4. Double click on `pc-to-mobile.bat` or run `python mover.py pc_to_mobile`.  
   
   Alternatively, if you don't want to use the script for whatever reason, you can do it manually (expand "Detailed manual guide" to read more on how to do it without the script).  
   
   <details><summary>Detailed manual guide</summary>
   
   Open <code>C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire\preferences</code> (or wherever your <code>preferences</code> folder is on PC), then copy <code>"STSDataDefect", "STSDataTheSilent", "STSDataVagabond", "STSTips", "STSDataWatcher", "STSUnlocks", "STSAchievements", "STSPlayer", "STSSaveSlots", "STSSeenBosses", "STSSeenCards", "STSSeenRelics", "STSUnlockProgress", "STSDaily", "STSBetaCardPreference"</code> to <code>Internal shared storage\Android\data\com.humble.SlayTheSpire\files\preferences</code> (or wherever your <code>files\preferences</code> is on android).  
   
   Also, move the <code>runs</code> folder in its entirety to move the history of runs. Each single run though has a local_time property that needs to be converted. Doing this by hand would be crazy, so if you don't want to use the script for whatever reason, write a script for at least doing that. On pc, it's local timezone (gmt+4) <code>%Y%m%d%H%M%S</code>. On mobile, it's UTC <code>%m/%d/%Y %H:%M:%S</code>. The name of the run is always a timestamp of when you played it.
   
   If you want to also move a save file of an active run (and you don't want to finish the run on whatever device you started it on) - they're xor encrypted with the key "key" on pc, but plaintext on mobile. Decode the base64, xor the raw bytes with "key", move the file.  
   </details>  
  
# Syncing from mobile to PC  

1. Check the `config.ini` file in the root directory of this project. Make sure to change the config parameters if they don't apply in your case.  
2. Make sure to enable USB debugging on your phone  
3. Connect your phone via USB to PC  
4. Double click on `mobile-to-pc.bat` or run `python mover.py mobile_to_pc`.  
   
   Alternatively, if you don't want to use the script for whatever reason, you can do it manually (expand "Detailed manual guide" to read more on how to do it without the script).  
   
   <details><summary>Detailed manual guide</summary>
   
   Essentially, do the inverse of the detailed manual guide for syncing from PC to mobile.  
   
   Move the specified pref files as is.  
   
   For the saves encode json text into bytes, then XOR the bytes with "key", and base64 encode the resulting bytes.  
   
   For each of the runs, don't forget to convert the local_time.  
   </details>  
  

# Troubleshooting  
  
### When transfering from PC to mobile, either parts from an old playthrough remain, or it just seems to have undone your sync?  
  
1. Go to the **Play Games** app on android ***__(NOT play store)__***, then `Settings > Your Data > Delete Play Games account & data > Delete individual game data > Slay the spire > delete`  
2. Turn on airplane mode  
3. Using the [**Files** app from **Marc apps & software**](https://play.google.com/store/apps/details?id=com.marc.files) (or using your USB connection, whichever works), go to `Internal shared storage\Android\data\com.humble.SlayTheSpire\files` (or whatever the path is on your phone) and delete everything in there, then create empty folders "preferences" and "saves". Note: if USB doesn't work and you don't have the app already - turn off airplane mode, install it, then repeat from step 1.
  
### When transfering from mobile to PC, either parts from an old playthrough remain, or it just seems to have undone your sync?  
  
1. There is a chance that steam's cloud saves might be causing you trouble, but I haven't encountered an issue like that yet so I haven't provided troubleshooting for that. You can find guides online for temporarily disabling steam cloud saves or accessing them and deleting them.  
2. That aside, to wipe the slate clean, go to the root directory of your slay the spire game on PC.   
You can find it by right-clicking on Slay the Spire on steam, then Properties -> Installed Files -> Browse.  
It should contain folders like "runs", "saves", "preferences", or files like SlayTheSpire.exe.  
3. Then, delete `runs`, `saves` and `preferences`.  
It's a good idea to back those up, as you may lose certain data like your settings (runs, for example, aren't even steam cloud synced).  
If you want to preserve your settings, delete `runs` and `saves` completely, but only delete the following files from `preferences`:  
`"STSDataDefect", "STSDataTheSilent", "STSDataVagabond", "STSTips", "STSDataWatcher", "STSUnlocks", "STSAchievements", "STSPlayer", "STSSaveSlots", "STSSeenBosses", "STSSeenCards", "STSSeenRelics", "STSUnlockProgress", "STSDaily", "STSBetaCardPreference"` (plus their corresponding `.backUp` files, as well).  
4. Create empty folders "preferences" and "saves".  
  
### The python code throws an error?
  
1. Read the error to see if it's something related to the configuration, or if the error is from the script.  
2. If the error is from the script, you'll need to troubleshoot the issue, but the easiest thing to check is to make sure your Python version is at least 3.9 (otherwise it won't work).
  
