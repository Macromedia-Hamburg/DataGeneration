from flask import Flask, render_template, request
from mimesis import Person
from mimesis.locales import Locale

app = Flask("name")
app.secret_key = "banan"

@app.route("/")
def startscreen():
    return render_template("startscreen.html")

@app.route("/testgen", methods =["GET"])
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

if __name__ == "__main__":
    app.run(debug=False)
