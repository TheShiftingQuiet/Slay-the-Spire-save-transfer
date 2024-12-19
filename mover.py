import os
import subprocess
import base64
import json
import re
import sys
from datetime import datetime, timedelta
import configparser

PREFS_TO_MOVE = [
    "STSDataDefect", "STSDataTheSilent", "STSDataVagabond", "STSTips",
    "STSDataWatcher", "STSUnlocks", "STSAchievements", "STSPlayer",
    "STSSaveSlots", "STSSeenBosses", "STSSeenCards", "STSSeenRelics",
    "STSUnlockProgress", "STSDaily", "STSBetaCardPreference"
]

AUTOSAVE_FILES = [
    "IRONCLAD.autosave", "DEFECT.autosave", "WATCHER.autosave", "THE_SILENT.autosave"
]

RUNS_DIRNAMES = [
    "IRONCLAD", "DEFECT", "WATCHER", "THE_SILENT"
]

XOR_KEY = "key"
TMP_PC_PATH = os.path.join(os.getcwd(), "tmp")

def load_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    config.read(config_path)
    return config["DEFAULT"]
    
def parse_time_offset(offset):
    """
    Parse a time offset string (e.g., +5:45, -4:25, 0) and convert it to decimal hours.

    :param offset: A string representing the time offset (e.g., +5:45, -4:25, 0, -4). Must be of the pattern [+/-]?[hours][:minutes]?
    :return: The offset in decimal hours as a float.
    :raises ValueError: If the input format is invalid.
    """

    pattern = r"^\s*([+-]?)(\d+)(:\d{1,2})?\s*$"  # Matches [+/-][hours][:minutes]
    match = re.match(pattern, offset)
    if not match:
        raise ValueError(f"Invalid timezone offset format: '{offset}'. Must be of the pattern [+/-]?[hours][:minutes]? (+ or - optional, hours required, a separator : and number of minutes optional).")
    
    sign_str, hours_str, minutes_part = match.groups()
    
    sign = -1 if sign_str == '-' else 1
    
    hours = int(hours_str)
    
    minutes = int(minutes_part[1:]) if minutes_part else 0
    
    if not (0 <= minutes < 60):
        raise ValueError(f"Invalid minutes value: '{minutes}' in offset '{offset}', must be between 0 and 60.")
    
    decimal_offset = hours + minutes / 60.0
    
    return sign * decimal_offset

def path_join_adb(*args):
    new_args = []
    args_len = len(args)
    for n, arg in enumerate(args, start=1):
        arg_modified = arg
        if n != 1:
            arg_modified = arg_modified.removeprefix('/')
        if n != args_len:
            arg_modified = arg_modified.removesuffix('/')
        new_args.append(arg_modified)
    return "/".join(new_args)


# on pc, it's local timezone (gmt+4) %Y%m%d%H%M%S
# on mobile, it's UTC %m/%d/%Y %H:%M:%S

def pc_to_mobile_timestamp(timestamp, timezone_offset_hours):
    dt_object = datetime.strptime(str(timestamp), '%Y%m%d%H%M%S')
    utc_dt_object = dt_object - timedelta(hours=timezone_offset_hours)
    return utc_dt_object.strftime('%m/%d/%Y %H:%M:%S')

def mobile_to_pc_timestamp(timestamp, timezone_offset_hours):
    dt_object = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S')
    local_dt_object = dt_object + timedelta(hours=timezone_offset_hours)
    return local_dt_object.strftime('%Y%m%d%H%M%S')


def validate_adb():
    try:
        subprocess.run(["adb", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ADB is installed and accessible.")
    except subprocess.CalledProcessError as e:
        print("ADB is not installed or not added to the PATH.")
        raise e
        
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, text=True)
    devices = result.stdout.splitlines()
    if len(devices) <= 1 or not any("device" in line for line in devices[1:]):
        raise Exception("No device connected. Please enable USB debugging on your android phone and connect it via USB.")


def push_files(pc_path, phone_path, files, must_exist=False):
    for file in files:
        pc_file_path = os.path.join(pc_path, file)
        phone_file_path = path_join_adb(phone_path, file)
        if os.path.exists(pc_file_path):
            print(f"Pushing {file} to the phone...")
            subprocess.run(["adb", "shell", "mkdir", "-p", phone_path], check=True)
            subprocess.run(["adb", "push", pc_file_path, phone_path], check=True)
            subprocess.run(["adb", "shell", "chmod", "660", phone_file_path], check=True)
            print(f"Successfully pushed {file}.")
        else:
            if must_exist:
                raise Exception(f"File {file} must exist in {pc_path}. Investigate why it isn't.")
                
            print(f"File {file} does not exist in {pc_path}. Skipping.")

def pull_files(phone_path, pc_path, files):
    for file in files:
        phone_file_path = path_join_adb(phone_path, file)
        pc_file_path = os.path.join(pc_path, file)
        print(f"Pulling {file} from the phone...")
        try:
            subprocess.run(["adb", "pull", phone_file_path, pc_file_path], check=True)
            print(f"Successfully pulled {file}.")
        except Exception:
            print(f"File {phone_file_path} does not exist. Skipping.")
        

def copy_runs_directory(runs_pc_dir, runs_phone_dir, timezone_offset_hours, direction):
    # local_time needs to be converted when moving from PC to phone and vice-versa or it crashes the game
    # there is also a difference in build_version, play_id and playtime, but I'm not sure what these are for 
    #   (I have some educated guesses) and they don't seem to crash anything so we just convert the local_time alone
    
    if direction == "pc_to_mobile":
        print(f"Copying 'runs' directory from PC to phone...")
        subprocess.run(["adb", "shell", "mkdir", "-p", runs_phone_dir], check=True)
        
        for char_folder in RUNS_DIRNAMES:
            pc_char_runs_dir = os.path.join(runs_pc_dir, char_folder)
            if not os.path.exists(pc_char_runs_dir):
                print(f"There is no history of runs for {char_folder} in {runs_pc_dir}. Skipping.")
                continue
            
            char_folder_phone = path_join_adb(runs_phone_dir, char_folder)
            subprocess.run(["adb", "shell", "mkdir", "-p", char_folder_phone], check=True)
            
            run_files = [filename for filename in os.listdir(pc_char_runs_dir) if os.path.isfile(os.path.join(pc_char_runs_dir, filename))]     
            for file_name in run_files:
                pc_orig_file_path = os.path.join(pc_char_runs_dir, file_name)
                with open(pc_orig_file_path, 'r') as f_orig:
                    run_data = json.load(f_orig)

                if 'local_time' in run_data:
                    run_data['local_time'] = pc_to_mobile_timestamp(run_data['local_time'], timezone_offset_hours)

                temp_file_path = os.path.join(TMP_PC_PATH, f"pc_{char_folder}_{file_name}")
                with open(temp_file_path, "w") as f_tmp:
                    json.dump(run_data, f_tmp, separators=(',', ':'))

                phone_file_path = path_join_adb(char_folder_phone, file_name)
                subprocess.run(["adb", "push", temp_file_path, phone_file_path], check=True)
                subprocess.run(["adb", "shell", "chmod", "660", phone_file_path], check=True)

    else:
        print(f"Copying 'runs' directory from phone to PC...")
        
        for char_folder in RUNS_DIRNAMES:
            phone_char_runs_dir = path_join_adb(runs_phone_dir, char_folder)
            pc_char_runs_dir = os.path.join(runs_pc_dir, char_folder)
            
            created_empty = False
            if not os.path.exists(pc_char_runs_dir):
                created_empty = True
                os.makedirs(pc_char_runs_dir)
            
            try:
                result = subprocess.run(["adb", "shell", "ls", phone_char_runs_dir], stdout=subprocess.PIPE, text=True, check=True)
            except Exception:
                print(f"There is no history of runs for {char_folder} in {runs_phone_dir}. Skipping.")
                if created_empty:
                    # it's empty and it didn't exist till we created it just now so it should be easily deleted
                    #   so that it's consistent with how it was before running this
                    os.rmdir(pc_char_runs_dir)
                continue

            run_files = result.stdout.splitlines()
            
            for file_name in run_files:
                if not file_name.strip():
                    continue
                
                phone_file_path = path_join_adb(phone_char_runs_dir, file_name)
                tmp_file_path = os.path.join(TMP_PC_PATH, f"mobile_{char_folder}_{file_name}")
                
                try:
                    subprocess.run(["adb", "pull", phone_file_path, tmp_file_path], check=True)
                except Exception as e:
                    print(f"Failed to pull {file_name} from {phone_file_path}. Error: {e}")
                    continue
                
                with open(tmp_file_path, "r") as f:
                    run_data = json.load(f)
                
                if 'local_time' in run_data:
                    run_data['local_time'] = mobile_to_pc_timestamp(run_data['local_time'], timezone_offset_hours)
                
                pc_file_path = os.path.join(pc_char_runs_dir, file_name)
                with open(pc_file_path, "w") as f:
                    json.dump(run_data, f, separators=(',', ':'))
                
                print(f"Successfully pulled and saved {file_name} to {pc_char_runs_dir}.")



# the save files (active run save files: you won't have them if you aren't in the middle of an unfinished run when you run this) are, 
#    for some reason, encoded to raw bytes from JSON, then XOR'd with the key "key", then base64'd on PC,
#    while on mobile they're plaintext json.

def decode_and_xor(file_path):
    with open(file_path, "r") as f:
        base64_data = f.read()
        decoded_data = base64.b64decode(base64_data)
        decoded_bytes = bytes(byte ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, byte in enumerate(decoded_data))
        return decoded_bytes.decode('utf-8')

def encode_and_xor(json_str):
    encoded_bytes = bytes(ord(char) ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, char in enumerate(json_str))
    return base64.b64encode(encoded_bytes).decode('utf-8')


def pull_encoded_json(phone_file_path, temp_file_path, pc_file_path):
    try:
        subprocess.run(["adb", "pull", phone_file_path, temp_file_path], check=True)
    except Exception:
        save_name = os.path.basename(phone_file_path)
        print(f"There is no autosave of an active run for {save_name} at {phone_file_path.removesuffix(save_name).removesuffix('/')}. Skipping.")
        return
    
    print(f"Pulling and encoding active run save JSON from {phone_file_path}...")
    with open(temp_file_path, "r") as f:
        json_data = json.load(f)
    encoded_data = encode_and_xor(json.dumps(json_data))
    with open(pc_file_path, "w") as f:
        f.write(encoded_data)
    print(f"Successfully encoded and saved {os.path.basename(pc_file_path)}.")

def main():
    config = load_config()

    prefs_pc_path = os.path.join(config["PcPathToGame"], "preferences")
    prefs_phone_path = path_join_adb(config["AndroidPathToGame"], "files/preferences")
    runs_pc_path = os.path.join(config["PcPathToGame"], "runs")
    runs_phone_path = path_join_adb(config["AndroidPathToGame"], "files/runs")
    saves_pc_path = os.path.join(config["PcPathToGame"], "saves")
    saves_phone_path = path_join_adb(config["AndroidPathToGame"], "files/saves")
    timezone_offset_hours = parse_time_offset(config["LocalTimezoneOffsetHours"])
    
    if len(sys.argv) != 2 or sys.argv[1] not in ("pc_to_mobile", "mobile_to_pc"):
        print("Usage: script.py <pc_to_mobile|mobile_to_pc>")
        return
        
    direction = sys.argv[1]
    
    if not os.path.exists(config["PcPathToGame"]):
        print(f"Invalid PcPathToGame, the directory {config['PcPathToGame']} doesn't exist. Please check the config file and ensure it points to the Slay the Spire root folder that contains runs and/or saves and/or preferences folders.")
        return
        
    prefs_pc_path_exists = os.path.exists(prefs_pc_path)
    runs_pc_path_exists = os.path.exists(runs_pc_path)
    saves_pc_path_exists = os.path.exists(saves_pc_path)
    
    if not any([prefs_pc_path_exists, runs_pc_path_exists, saves_pc_path_exists]):
        print(f"Invalid PcPathToGame, the directory {config['PcPathToGame']} exists, but it contains neither a folder 'saves', nor 'runs', nor 'preferences'. Please launch the game at least once to let these folders generate, or create at least one empty folder for them, this is a security check to ensure you're not accidentally pulling data to the wrong directory. Please check the config file and ensure it points to the Slay the Spire root folder that contains runs and/or saves and/or preferences folders.")
        return
       
    for exists_, path_ in [(prefs_pc_path_exists, prefs_pc_path), (runs_pc_path_exists, runs_pc_path), (saves_pc_path_exists, saves_pc_path)]:
        if not exists_:
            os.mkdir(path_)
    
    validate_adb()
    
    subprocess.run(["adb", "shell", "mkdir", "-p", prefs_phone_path], check=True)
    subprocess.run(["adb", "shell", "mkdir", "-p", runs_phone_path], check=True)
    subprocess.run(["adb", "shell", "mkdir", "-p", saves_phone_path], check=True)

    if not os.path.exists(TMP_PC_PATH):
        os.mkdir(TMP_PC_PATH)
        
    autosaves_temp_path = os.path.join(TMP_PC_PATH, "pc_autosaves" if direction == "pc_to_mobile" else "mobile_autosaves")
    if not os.path.exists(autosaves_temp_path):
        os.mkdir(autosaves_temp_path)
        
    if direction == "pc_to_mobile":           
        push_files(prefs_pc_path, prefs_phone_path, PREFS_TO_MOVE)
        copy_runs_directory(runs_pc_path, runs_phone_path, timezone_offset_hours, direction)
        for autosave_file in AUTOSAVE_FILES:
            pc_file_path = os.path.join(saves_pc_path, autosave_file)
            if not os.path.exists(pc_file_path):
                print(f"There is no autosave of an active run for {autosave_file} at {saves_pc_path}. Skipping.")
                continue
                
            decoded_str = decode_and_xor(pc_file_path)
            temp_file_path = os.path.join(autosaves_temp_path, autosave_file)
            with open(temp_file_path, "w") as f:
                f.write(decoded_str)
            push_files(autosaves_temp_path, saves_phone_path, [autosave_file], must_exist=True)
    else:
        pull_files(prefs_phone_path, prefs_pc_path, PREFS_TO_MOVE)
        copy_runs_directory(runs_pc_path, runs_phone_path, timezone_offset_hours, direction)
        for autosave_file in AUTOSAVE_FILES:
            pc_file_path = os.path.join(saves_pc_path, autosave_file)
            temp_file_path = os.path.join(autosaves_temp_path, autosave_file)
            pull_encoded_json(path_join_adb(saves_phone_path, autosave_file), temp_file_path, pc_file_path)
    
    print("\n\nAll done! It's recommended for you to delete the contents of the 'tmp' folder now (in the same directory as the script). This isn't done automatically just in case you want to take a look at the temporary files or to troubleshoot something.")

if __name__ == "__main__":
    main()