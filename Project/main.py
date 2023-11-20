import os
import shutil
import tempfile

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


@app.route("/upload_json", methods=["POST"])
def upload_json():
    jsondata = "temp.json"

    # Kontaktstelle zum HTML Code. Erstellt eine Variable file und weißt dieser die Hochgeladene Datei zu
    file = request.files["file"]

    # Überprüft ob eine JSON Datei ausgewählt wurde, gibt einen Error zurück falls nicht
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

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

        # Temporäre Rückmeldungen/////////// MUSS NOCH DURCH RICHTIGE ERSETZT WERDEN SOBALD DATEIN GENERIERT WERDEN
        return jsonify({"message": "File successfully uploaded and processed."}), 200

    else:
        return jsonify({"error": "Invalid file format. Please upload a .json file."}), 400


if __name__ == "__main__":
    app.run(debug=False)