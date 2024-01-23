import os
import uuid
import random
import string
import shutil
import tempfile
import json
import glob
import time
import sys
from flask import Flask, render_template, request, jsonify, redirect, session
from mimesis import Person, Generic, Datetime
from mimesis.enums import Gender
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
        anzahl = request.form.get("anzahl")
        groesse = request.form.get("groesse")

        session["anzahl"] = anzahl
        session["groesse"] = groesse

        print(anzahl)
        print(groesse)

        return redirect("/brokendata")

    return render_template("Datensatz.html")

@app.route("/brokendata", methods=["POST", "GET"])
def brokendata():

    if request.method == "POST":

        brokendataPercentage = request.form.get('brokendataPercentage')
        emptydataPercentage = request.form.get('emptydataPercentage')

        session["brokendataPercentage"] = brokendataPercentage
        session["emptydataPercentage"] = emptydataPercentage

        print(brokendataPercentage)
        print(emptydataPercentage)

        return redirect("/Frequenz")

    return render_template("brokendata.html")

@app.route("/Frequenz", methods=["POST", "GET"])
def Frequenzscreen():
    if request.method == "POST":

        minutes = request.form.get('minutes')
        seconds = request.form.get('seconds')

        session['minutes'] = minutes
        session['seconds'] = seconds

        print(minutes)
        print(seconds)

        return redirect("/Distribution")

    return render_template("Frequenz.html")


@app.route("/Distribution", methods=["POST", "GET"])
def Distributionsscreen():

    dic = "mimesis.json"

    if request.method == "POST":
        distribution_data = {}

        for key in request.form:
            if key.endswith("_distribution"):
                field_name = key.replace("_distribution", "")
                distribution_data[field_name] = request.form[key]

        session['distribution_data'] = distribution_data

        print(distribution_data)

        return redirect("/exampledownload")

    with open(dic, "r") as json_file:
        mimesis_schema = json.load(json_file)

    simplified_keys = simplify_mimesis_schema(mimesis_schema)

    if len(simplified_keys) == 0:
        return redirect("/exampledownload")

    return render_template("Distribution.html", dic=simplified_keys)


@app.route("/exampledownload", methods=["POST", "GET"])
def exampledownload():

    if request.method == "POST":
        anzahl = session.get("anzahl")
        anzahl = int(anzahl)
        groesse = session.get("groesse")
        groesse = int(groesse)
        minutes = session.get("minutes")
        seconds = session.get("seconds")

        # Download button startet den Download
        final_generate(anzahl, groesse)

        # Startet den upload
        # AWS S3 Upload über for loop

        # Frequenz nach jedem upload (innerhalb des for loops)
        # frequenz(minutes, seconds)

        return redirect("/endscreen")


    with open("mimesis.json", 'r') as file:
        schema = json.load(file)
    datapack = [generate_data(schema)]
    # Generate 1 Datapack to showcase
    return render_template("exampledownload.html", datapack=datapack)


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

            elif value["type"] == "integer" or value["type"] == "number" or value["type"] == "int":
                result[key] = "int"
            elif value["type"] == "boolean":
                result[key] = "boolean"
            if "enum" in value:
                result[key] = {"choice": value["enum"]}
            if "minItems" in value and "maxItems" in value:
                result[key] = [process_properties(value["items"])] * value["maxItems"]

        return result

    return process_properties(json_schema.get("properties", {}))


#Nur Zahlen in die Distribution mit übernehmen
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
        elif isinstance(value, str) and value == "int":
            # Fügt den aktuellen Key wert der Liste hinzu, wenn es sich um einen int handelt
            simple_keys.append(current_key)

    return simple_keys

# Generate Data by Scheme
def generate_data(schema, generic=Generic('de')):
    distribution_data = session.get("distribution_data")

    def process_int(key, distribution_data):

        value = distribution_data.get(key, "Normal")

        if value == "Normal":
            return generic.random.randint(100000, 999999)
        if value == "Niedrig":
            return generic.random.randint(100000, 399999)
        if value == "Mittig":
            return generic.random.randint(400000, 699999)
        if value == "Hoch":
            return generic.random.randint(700000, 999999)
        if value == "Niedrig-Mittig":
            return generic.random.randint(100000, 699999)
        if value == "Mittig-Hoch":
            return generic.random.randint(400000, 999999)
        if value == "Niedrig-Hoch":

            gen_int = generic.random.randint(100000, 999999)
            while 400000 <= gen_int <= 699999:
                gen_int = generic.random.randint(100000, 999999)
            return gen_int

    def process_schema(key, value):
        fehlerliste = [123, "Nicht Gefunden", [" "], {" ": " "}]

        brokendataPercentage = session.get("brokendataPercentage")
        brokendataPercentage = int(brokendataPercentage)
        emptydataPercentage = session.get("emptydataPercentage")
        emptydataPercentage = int(emptydataPercentage)

        if random.randint(1, 100) <= brokendataPercentage:
            return str(random.choice(fehlerliste))
        elif random.randint(1, 100) <= emptydataPercentage:
            return None
        else:
            if isinstance(value, dict):
                if 'choice' in value:
                    return str(generic.random.choice(value['choice']))
                else:
                    result = {}
                    for k, v in value.items():
                        result[k] = process_schema(k, v)
                    return str(result)
            elif isinstance(value, list):
                return str([process_schema(i, item) for i, item in enumerate(value)])
            elif value == "text":
                return str(''.join(random.choices(string.ascii_letters + string.digits, k=10)))
            elif value == "boolean":
                return str(generic.random.choice([True, False]))
            elif value == "int":
                return str(process_int(key, distribution_data))
            elif value == "uuid":
                return str(uuid.uuid4())
            elif value == "date":
                dt = Datetime()
                return str(dt.date())
            elif value == "email":
                person = Person()
                return str(person.email())
            else:
                return f"Unbekannter Datentyp: {value}"

    if isinstance(schema, dict):
        result = {}
        for k, v in schema.items():
            result[k] = process_schema(k, v)
        return result
    elif isinstance(schema, list):
        return [process_schema(i, item) for i, item in enumerate(schema)]
    else:
        return f"Ungültiger Schematyp: {schema}"

def clear_previous_files():
    for file in glob.glob("generated_data_*.json"):
        os.remove(file)

def generate_large_data_file(anzahl_datensaetze):
    large_data = []

    with open("mimesis.json", "r") as json_file:
        mimesis_data = json.load(json_file)

    for _ in range(anzahl_datensaetze):
        large_data.append(generate_data(mimesis_data))

    with open("generated_data_large.json", "w") as json_file:
        json.dump(large_data, json_file, indent=2)

    return large_data

def split_data_into_smaller_files(large_data, zielgroesse_mb):
    file_index = 1
    buffer = ""
    buffer_size_mb = 0

    for record in large_data:
        serialized_record = json.dumps(record, indent=2)
        record_size_mb = len(serialized_record.encode('utf-8')) / (1024 * 1024)

        if buffer_size_mb + record_size_mb > zielgroesse_mb:
            generateddatapath = f"generated_data_{file_index}.json"
            with open(generateddatapath, "w") as json_file:
                json_file.write(buffer)

            file_index += 1
            buffer = serialized_record + "\n"
            buffer_size_mb = record_size_mb
        else:
            buffer += serialized_record + "\n"
            buffer_size_mb += record_size_mb

    if buffer:
        generateddatapath = f"generated_data_{file_index}.json"
        with open(generateddatapath, "w") as json_file:
            json_file.write(buffer)

    return file_index

def final_generate(data_amount, data_size):
    clear_previous_files()
    large_data = generate_large_data_file(data_amount)
    split_data_into_smaller_files(large_data, data_size)
    os.remove("generated_data_large.json")

def frequenz(minutes, seconds):
    time_frequency = minutes * 60 + seconds
    round(time_frequency)
    time.sleep(time_frequency)

if __name__ == "__main__":
    app.run(debug=True)
