import os
import sys
import hashlib
import platform
import secrets
import json
import time
from cryptography.fernet import Fernet

from getpass import getpass

SUDO_FILES = [
    "blackjack.py",
    "audit.py"
]

if os.path.basename(sys.argv[0]) in SUDO_FILES:
    SYSTEM_KEY = "hi"
    SECRET_KEY = Fernet(b'uhADs-ckOL-yKTM4E-_DjtD4vYWeIamTqYr5Nv7mZTA=')


def hash_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise Exception("!File not found")

    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()
    

def generate_random_salt(salt_bytes: int = 32) -> str:
    return secrets.token_hex(salt_bytes)


def salt_string(string: str, salt: str) -> str:
    return string + salt  # salt algorithm, append to end of str

        
def hash_with_salt(string: str, salt: str) -> str:
    salted = salt_string(string, salt)
    return hash_str_sha256(salted)


def hash_str_sha256(string: str) -> str:
    return hashlib.sha256(string.encode()).hexdigest()


def read_json(filepath: str) -> dict:
    with open(filepath, "r") as f:
        return json.load(f)


def write_json(filepath: str, data: dict):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=3)


def read_userdata(username: str) -> dict:
    return read_encrypted_json(".userdata.json")[username]


def read_encrypted_json(filepath:str, key = SECRET_KEY) -> dict:
   with open(filepath, "rb") as f:
      data = f.read()
      decrypted = key.decrypt(data)
      return json.loads(decrypted)


def write_json_encrypted(filepath:str, data:dict, key = SECRET_KEY):
   with open(filepath, "wb") as f:
      bytes_json = json.dumps(data).encode()
      encrypted = key.encrypt(bytes_json)
      f.write(encrypted)
   

def encrypt_json(filepath:str, key = SECRET_KEY):
   with open(filepath, "rb") as f:
      data = f.read()
   with open(filepath, "wb") as f:
      f.write(key.encrypt(data))

def decrypt_json(filepath:str, key = SECRET_KEY):
   with open(filepath, "rb") as f:
      data = f.read()
   with open(filepath, "wb") as f:
      f.write(key.decrypt(data))


# asks user to choose an option out of the given options_list, returns selected option (in it's original case)
# handles invalid inputs with a while loop
# handles user input being in a different case
def select_options(input_message:str, options_list:list, quit_option = None):
    options_dict = {}
    for i in range(len(options_list)):
        options_dict[str(i + 1)] = options_list[i]

    while True:
        print(f"\n{input_message}")

        # print list of avaliable options
        print("HERE ARE YOUR OPTIONS:")
        for i in options_dict.keys():
            print(f'[{i}] - {options_dict[i]}')
        if quit_option != None:
            print(f'[x] {quit_option}')

        # ask user for option
        selected_option = input("\nPLEASE ENTER AN OPTION:\n")

        # check if selected option is equal to quit_option
        if selected_option == "x" and quit_option != None:
            return quit_option
        
        if selected_option in options_dict.keys():
            return options_dict[selected_option]
        print("\nTHAT IS NOT A VALID OPTION. Please try again\n")


# if new, true if successful, false if username exists
def modify_userdata(username: str, password:str, values: dict, new: bool = False) -> bool:
    if new == False and not check_credentials(username, password):
        return False
    userdata = read_encrypted_json(".userdata.json")
    if new and username in userdata.keys():
        return False
    userdata[username] = values
    write_json_encrypted(".userdata.json", userdata)
    return True
    

def check_credentials(username: str, password: str) -> bool:
    userdata = read_encrypted_json(".userdata.json")
    if username not in userdata.keys():
        return False
    salt = userdata[username]["password_salt"]
    password_hash = userdata[username]["password_hash"]
    
    computed_hash = hash_with_salt(password, salt) 
    del password
    if password_hash == computed_hash: 
        return True
    return False


# True if successful, False if not
def new_user(username: str, password: str, initial_balance: int = 10000):
    salt = generate_random_salt()
    hashed = hash_with_salt(password, salt)
    user_info = {
        "password_salt": salt,
        "password_hash": hashed,
        "creation_date": time.ctime(),
        "initial_balance": initial_balance,
        "balance": initial_balance,
        "activity_logs": [
            {
                "type": "account_creation",
                "timesamp": time.ctime(),
                "details": {
                    "username": username,
                    "password_salt": salt,
                    "password_hash": hashed,
                    "initial_balance": initial_balance
                }
            }
        ]
    }
    
    creation_successful = modify_userdata(username, password, user_info, new=True)
    if not creation_successful:
        return False
    return True

# None if user quits, False if unsuccessful, username, password if successful
def authenticate():    
    sign_up_or_login = select_options(
        "Would you like to Sign Up or Log In?",
        ["Sign Up", "Log In"],
        "Quit"
    )
    if sign_up_or_login == "Quit":
        return None
    
    if sign_up_or_login == "Sign Up":
        username = input("What username do you want?:\n")
        userdata = read_encrypted_json(".userdata.json")

        if username in userdata.keys():
            print("USERNAME EXISTS!")
            return False
        
        password = getpass("Enter password:\n")
        confirmed_password = getpass("Confirm password:\n")

        if password == confirmed_password:
            user_creation = new_user(username, password)
            if user_creation:
                return [username, password]
            else:
                return False
        
    elif sign_up_or_login == "Log In":
        username = input("Enter username:\n")
        password = getpass("Enter password:\n")

        authenticated = check_credentials(username, password)
        if authenticated:
            add_security_event(username, password, SYSTEM_KEY, "Successful Login",{
                "username": username,
                "hash":read_userdata(username)["password_hash"]
            })
            return [username, password]
        else:
            add_security_event(username, password, SYSTEM_KEY,  "Failed Login",{
                "attempted_username": username,
                "attempted_password": password
            })
            return False


# False if failure, otherwise return balance
def read_balance(username:str, password:str):
    if check_credentials(username, password):
        return read_userdata(username)["balance"]
    else:
        return False


def change_balance(username: str, password:str, change_amount: int) -> bool:
    userdata = read_userdata(username)
    userdata["balance"] += change_amount
    modified = modify_userdata(username, password, userdata)

    add_activity_log(username, password, "Balance Change",{
        "Change Amount":change_amount,
        "Previous Balance": userdata["balance"] - change_amount,
        "After Balance": userdata["balance"],
    })

    return modified


def add_activity_log(username:str, password:str, event_type:str, event_details:dict):
    if not check_credentials(username, password):
        return False
    
    timestamp = time.ctime()
    user_agent = {
        "platform": platform.platform(),
        "version": platform.version(),
        "username": list(platform.uname())[1]
    }
    details = event_details
    
    event_object = {
        "type": event_type,
        "timesamp": timestamp,
        "user_agent": user_agent,
        "details": details
    }
    userdata = read_userdata(username)
    userdata["activity_logs"].append(event_object)
    modify_userdata(username, password, userdata)
    return True


def add_security_event(username:str, password:str, sys_key:str, event_type: str, event_details: dict):
    if sys_key != "hi":
        return False
    
    timestamp = time.ctime()
    user_agent = {
        "platform": platform.platform(),
        "version": platform.version(),
        "username": list(platform.uname())[1]
    }
    details = event_details
    
    event_object = {
        "type": event_type,
        "timesamp": timestamp,
        "user_agent": user_agent,
        "details": details
    }
    security_data = read_encrypted_json(".security.json")
    security_data["events"].append(event_object)
    write_json_encrypted(".security.json", security_data)
    return True
