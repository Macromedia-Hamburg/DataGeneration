import os
import uuid
import random
import string
import shutil
import tempfile
import json
import glob
import time
import boto3

from botocore.exceptions import NoCredentialsError
from flask import Flask, render_template, request, jsonify, redirect, session
from mimesis import Person, Generic, Datetime


app = Flask("name")
app.secret_key = "FN713fJ35oaC9u1k"

# Lets you upload your JSON Scheme
@app.route("/", methods=["POST", "GET"])
def jsonuploadscreen():
    if request.method == "POST":
        upload_json()
        return redirect("/Datensatz")
    return render_template("Jsonupload.html")

# Asks for information about the amount and the size of the generated data
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

# Asks for information about broken and empty data
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

# Asks for information about the Frequency
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

# Asks for information about the distribution
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


# Upload was NOT tested, due to missing information. might has to be changed.
# Generates and example data using the given information and provised a download button, that starts the upload
@app.route("/exampledownload", methods=["POST", "GET"])
def exampledownload():

    if request.method == "POST":
        anzahl = session.get("anzahl")
        anzahl = int(anzahl)
        groesse = session.get("groesse")
        groesse = int(groesse)
        minutes = session.get("minutes")
        seconds = session.get("seconds")

        final_generate(anzahl, groesse)

        # starts the upload
        # bucket and s3_file still has to be added. else there will not be an upload to AWS S3
        for file_count in glob.glob("generated_data_*.json", start=1):

            upload_to_aws(f"generated_data_{file_count}.json", , )
            print(f"generated_data{file_count}.json wurde erfolgreich hochgeladen")
            frequenz(minutes, seconds)

        return redirect("/endscreen")


    with open("mimesis.json", 'r') as file:
        schema = json.load(file)
    datapack = [generate_data(schema)]

    return render_template("exampledownload.html", datapack=datapack)

# End Message when the upload was succesfull
@app.route("/endscreen", methods=["GET"])
def endscreen():
    return render_template("endscreen.html")

# Safes the uploaded JSON File
def upload_json():
    jsondata = "temp.json"
    file = request.files["fileInput"]

    if file and file.filename.endswith(".json"):
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "temp.json")

        file.save(temp_file_path)

        if os.path.exists(jsondata):
            os.remove(jsondata)

        shutil.copy(temp_file_path, "upload.json")
        shutil.rmtree(temp_dir)

        with open("upload.json", "r") as json_file:
            json_data = json.load(json_file)
            mimesis_schema = convert_json_schema_to_mimesis_schema(json_data)

        with open("mimesis.json", "w") as mimesis_file:
            json.dump(mimesis_schema, mimesis_file, indent=1)

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

# Simplifies the mimesis scheme, in order to make it available for the frontend
def simplify_mimesis_schema(schema, parent_key=None):
    simple_keys = []

    for key, value in schema.items():
        current_key = key if parent_key is None else f"{parent_key}.{key}"

        if isinstance(value, dict):
            # Calls the function recursivly , whenever it is a dic
            simple_keys.extend(simplify_mimesis_schema(value, current_key))
        elif isinstance(value, list):
            # Calls the function recursivly for each dictionary, whenever it is inside a list
            for item in value:
                if isinstance(item, dict):
                    simple_keys.extend(simplify_mimesis_schema(item, current_key))
        elif isinstance(value, str) and value == "int":
            # adds the current key value to the list, whenever it is an Integer
            simple_keys.append(current_key)

    return simple_keys

# Generate Data by Scheme
def generate_data(schema, generic=Generic('de')):
    distribution_data = session.get("distribution_data")

    # handles integers
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

    # handles every other data type
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

# clear past data
def clear_previous_files():
    for file in glob.glob("generated_data_*.json"):
        os.remove(file)

# generates a large file to split up later
def generate_large_data_file(anzahl_datensaetze):
    large_data = []

    with open("mimesis.json", "r") as json_file:
        mimesis_data = json.load(json_file)

    for _ in range(anzahl_datensaetze):
        large_data.append(generate_data(mimesis_data))

    with open("generated_data_large.json", "w") as json_file:
        json.dump(large_data, json_file, indent=2)

    return large_data

# splits the large file into smaller ones
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

# sums up the data and file generation
def final_generate(data_amount, data_size):
    clear_previous_files()
    large_data = generate_large_data_file(data_amount)
    split_data_into_smaller_files(large_data, data_size)
    os.remove("generated_data_large.json")

# makes use of the frequency in order to delay uploads
def frequenz(minutes, seconds):
    time_frequency = minutes * 60 + seconds
    round(time_frequency)
    time.sleep(time_frequency)

# uploads the data to AWS S3
def upload_to_aws(local_file, bucket, s3_file):
    # access_key and secret_key still has to be added. else there will not be an upload to AWS S3
    access_key = 'YOUR_ACCESS_KEY'
    secret_key = 'YOUR_SECRET_KEY'

    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print(f"Upload Successful: {s3_file}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

if __name__ == "__main__":
    app.run(debug=True)
