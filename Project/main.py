import os
import shutil
import tempfile
import json

from flask import Flask, render_template, request, jsonify, redirect
from mimesis import Person
from mimesis.locales import Locale

app = Flask("name")
app.secret_key = "banan"


@app.route("/", methods=["POST", "GET"])
def jsonuploadscreen():
    if request.method == "POST":
        upload_json()
        return redirect("/Datensatz")
    return render_template("Jsonupload.html")


@app.route("/Datensatz", methods=["POST", "GET"])
def datensatzscreen():
    if request.method == "POST":
        # Hier Code implimentieren
        return redirect("/Distribution")

    return render_template("Datensatz.html")


@app.route("/Frequenz", methods=["POST", "GET"])
def Frequenzscreen():
    if request.method == "POST":
        # Hier Code implimentieren
        return redirect("/Distribution")

    return render_template("Frequenz.html")


@app.route("/Distribution", methods=["POST", "GET"])
def Distributionsscreen():

    dic = "mimesis.json"

    if request.method == "POST":
        return redirect("/exampledownload")

    # Logik der Distribution fehlt noch. Je nach Auswahl auf der Seite muss das generieren beeinflusst werden
    with open(dic, "r") as json_file:
        mimesis_schema = json.load(json_file)

    simplified_keys = simplify_mimesis_schema(mimesis_schema)

    return render_template("Distribution.html", dic=simplified_keys)


@app.route("/exampledownload", methods=["POST", "GET"])
def Downloadscreen():

    if True:
        #hier Code implimentieren
        return redirect("/endscreen")

    return render_template("exampledownload.html")


@app.route("/endscreen", methods=["GET"])
def endscreen():
    return render_template("endscreen.html")


def upload_json():
    jsondata = "temp.json"

    # Kontaktstelle zum HTML Code. Erstellt eine Variable file und weißt dieser die Hochgeladene Datei zu
    file = request.files["fileInput"]

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

        # Liest den inhalt der upload.json
        with open("upload.json", "r") as json_file:
            json_data = json.load(json_file)
            mimesis_schema = convert_json_schema_to_mimesis_schema(json_data)

        # Speichert den inhalt der upload.json als mimesis schema
        with open("mimesis.json", "w") as mimesis_file:
            json.dump(mimesis_schema, mimesis_file, indent=1)

        # Temporäre Rückmeldungen/////////// MUSS NOCH DURCH RICHTIGE ERSETZT WERDEN SOBALD DATEIN GENERIERT WERDEN
        return jsonify({"message": "File successfully uploaded and processed."}), 200


# Nested Function zur umwandlung eines Json Schemas in ein Mimesis Schema
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


if __name__ == "__main__":
    app.run(debug=False)
