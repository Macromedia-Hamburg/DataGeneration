#### Coverter #####

def convert_json_schema_to_mimesis_schema(json_schema):
    def process_properties(properties):
        result = {}
        for key, value in properties.items():
            if value["type"] == "object":
                result[key] = process_properties(value.get("properties", {}))
            elif value["type"] == "array":
                result[key] = [process_properties(value["items"]["properties"])] if "properties" in value["items"] else "text"
            elif value["type"] == "string":
                if "format" in value:
                    if "date" in value["format"]:
                         result[key] = "date"
                    elif value["format"] == "uuid":
                        result[key] = "uuid"
                    elif value["format"] == "email":
                        result[key] = "email"
                else:
                    result[key] = "text"

            elif value["type"] == "integer" or value["type"] == "number":
                result[key] = "number"
            elif value["type"] == "boolean":
                result[key] = "boolean"
            if "enum" in value:
                result[key] = {"choice": value["enum"]}
            if "minItems" in value and "maxItems" in value:
                result[key] = [process_properties(value["items"])] * value["maxItems"]

        return result

    return process_properties(json_schema.get("properties", {}))



def simplify_mimesis_schema(schema, parent_key=None):
    simple_keys = []

    for key, value in schema.items():
        current_key = key if parent_key is None else f"{parent_key}.{key}"

        if isinstance(value, dict):
            # Ruft die Funktion rekursiv auf, wenn es sich um ein Dic handelt
            simple_keys.extend(simplify_mimesis_schema(value, current_key))
        elif isinstance(value, list):
            # Ruft die funktion für jedes Dic rekursiv auf, wenn es sich in einer Liste befindet
            for item in value:
                if isinstance(item, dict):
                    simple_keys.extend(simplify_mimesis_schema(item, current_key))
        elif isinstance(value, str):
            # Fügt den aktuellen Key wert der Liste hinzu, wenn es sich um eine variable handelt
            simple_keys.append(current_key)

    return simple_keys



def write_mimesis_schema_to_file(mimesis_schema, file_path):
    with open(file_path, 'w') as file:
        json.dump(mimesis_schema, file, indent=4)

# Hauptteil
if __name__ == "__main__":
    input_json_file = r"C:\Users\jango\Desktop\S3\Softwareprojekt1\Schema_hard2.json"  # Raw string for file path
    output_mimesis_file = r"C:\Users\jango\Desktop\S3\Softwareprojekt1\output.json"  # Include file name

    json_schema = read_json_file(input_json_file)
    mimesis_schema = convert_json_schema_to_mimesis_schema(json_schema)
    write_mimesis_schema_to_file(mimesis_schema, output_mimesis_file)

    print("Mimesis Schema wurde erfolgreich erstellt und gespeichert.")





#### Generating #####



import uuid
import random
import string 
import json
from mimesis import Generic
from mimesis.enums import Gender
from mimesis import Datetime 
from mimesis import Person 

def generate_data(schema, generic=Generic('de')):
    if isinstance(schema, dict):
        # Check if the dictionary has a 'choice' key
        if 'choice' in schema:
            # If 'choice' key is present, select randomly from the choices
            return generic.random.choice(schema['choice'])
        else:
            # If not, recursively process each key-value pair in the dictionary
            return {key: generate_data(value, generic) for key, value in schema.items()}
    elif isinstance(schema, list):
        return [generate_data(item, generic) for item in schema]
    elif schema == "text":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    elif schema == "boolean":
        return generic.random.choice([True, False])
    elif schema == "number":
        return generic.person.age()
    elif schema == "uuid":
        return uuid.uuid4()
    elif schema =="date":
        dt = Datetime()
        return dt.date()
    elif schema =="email":
        person = Person()
        return person.email()
    
    else:
        return f"Unbekannter Datentyp: {schema}"







# Datei öffnen
with open('C:\\Users\\jango\\Desktop\\S3\\Softwareprojekt1\\output.json', 'r') as file:
    liste_mimesis = json.load(file)


# Jetzt enthält `liste_mimesis` die Daten aus der JSON-Datei
# Du kannst mit dieser Liste weiterarbeiten, wie du möchtest

schema = liste_mimesis

# Daten generieren
fake_data = generate_data(schema)
print(fake_data)

