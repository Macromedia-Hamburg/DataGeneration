import os
import shutil
import tempfile
import json

from flask import Flask, render_template, request, jsonify
from mimesis import Person
from mimesis.locales import Locale

app = Flask("name")
app.secret_key = "banan"


@app.route("/", methods=["GET"])
def testgen():
    # Gibt die Region der Person an
    person = Person(Locale.EN)

    # Generiert die Beispieldaten
    first_name = person.first_name()
    last_name = person.last_name()
    address_data = person.nationality()
    telephone = person.phone_number()
    email = person.email(unique=True)
    gender = person.gender()
    age = person.age(minimum=18, maximum=80)

    data = {
        "Vorname": first_name,
        "Nachname": last_name,
        "Nationalität": address_data,
        "Telefonnummer": telephone,
        "E-Mail": email,
        "Geschlecht": gender,
        "Alter": age
    }

    return render_template("testgen.html", data=data)


@app.route("/upload_json", methods=["PUT"])
def upload_json():
    jsondata = "temp.json"

    # Kontaktstelle zum HTML Code. Erstellt eine Variable file und weißt dieser die Hochgeladene Datei zu
    file = request.files["file"]

    # Wird ausgeführt wenn eine JSON Datei ausgewählt wurde. Erstellt einen temporären Dateipfad für die temp.json Datei
    if file and file.filename.endswith(".json"):
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "temp.json")

        # Speichert die hochgeladene Datei im temporären Verzeichnis
        file.save(temp_file_path)

        # Überprüft ob temp.json erstellt wurde und falls ja, wird diese gelöscht
        if os.path.exists(jsondata):
            os.remove(jsondata)

        # Kopiert den Inhalt der Temp Datei in die uploaddata.json im Dateiordner
        shutil.copy(temp_file_path, "upload.json")

        # Leert das Temporäre Verzeichnis
        shutil.rmtree(temp_dir)

        #Liest den inhalt der upload.json
        with open("upload.json", "r") as json_file:
            json_data = json.load(json_file)
            mimesis_schema = convert_json_schema_to_mimesis_schema(json_data)

        #Speichert den inhalt der upload.json als mimesis schema
        with open("mimesis.json", "w") as mimesis_file:
            json.dump(mimesis_schema, mimesis_file, indent=1)

        # Temporäre Rückmeldungen/////////// MUSS NOCH DURCH RICHTIGE ERSETZT WERDEN SOBALD DATEIN GENERIERT WERDEN
        return jsonify({"message": "File successfully uploaded and processed."}), 200

#Nested Function zur umwandlung eines Json Schemas in ein Mimesis Schema
def convert_json_schema_to_mimesis_schema(json_schema):
    def process_properties(properties):
        result = {}
        for key, value in properties.items():
            if value["type"] == "object":
                result[key] = process_properties(value.get("properties", {}))
            elif value["type"] == "array":
                result[key] = [process_properties(value["items"])]
            elif value["type"] == "string":
                result[key] = "text"
                if "format" in value:
                    result[key] = value["format"]
            elif value["type"] == "integer":
                result[key] = "age"
            elif value["type"] == "boolean":
                result[key] = "boolean"
            if "enum" in value:
                result[key] = {"choice": value["enum"]}
            if "minItems" in value and "maxItems" in value:
                result[key] = [process_properties(value["items"])] * value["maxItems"]

        return result

    return process_properties(json_schema.get("properties", {}))

if __name__ == "__main__":
    app.run(debug=False)
