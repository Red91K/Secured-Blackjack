from security import *

log_types = {
   "security": ".security.json",
   "userdata": ".userdata.json"
}

while True:
   usr_input = input("Enter log type to extract:\n").lower()
   if usr_input in log_types:
      break
   else:
      print("INVALID INPPUT")

out_filename = usr_input + " log - " + time.ctime() + ".json"
filename = log_types[usr_input]

log_data = read_encrypted_json(filename)
write_json(out_filename, log_data)
