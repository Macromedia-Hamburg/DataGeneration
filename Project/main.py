from flask import Flask, render_template, request, session
from mimesis import Person
from mimesis.locales import Locale
import json

app = Flask("name")
app.secret_key = "banan"

@app.route("/", methods =["GET"])
def testgen():

    person = Person(Locale.EN)

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

def readscheme():
    # read json scheme

    # temp json erstellen, in dem der inhalt der json scheme zwischengespeichert wird
    pass

"""
@app.route("/upload", methods=["POST"])
def upload():
    global uploaded_file_content

    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    uploaded_file_content = file.read().decode("utf-8")
"""

if __name__ == "__main__":
    app.run(debug=False)