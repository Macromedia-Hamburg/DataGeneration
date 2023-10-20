
import json

# Create test JSON file
data = {
    "name": "Jan",
    "age": 20,
    "city": "Hamburg",
}

with open("data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

# Reading JSON Input
json_name = input("JSON FILE NAME: ")
try:
    with open(json_name, "r") as json_file:
        content = json.load(json_file)
except FileNotFoundError:
    print(f"The file '{json_name}' does not exist.")


print(json.dumps(content, indent=4))

# Clearing Values
for key in content:
    content[key] = None

# Create new JSON with the same format (empty values), means format is saved
with open("new_data.json", "w") as json_file2:
    json.dump(content, json_file2, indent=4)
