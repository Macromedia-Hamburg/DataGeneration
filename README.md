
# DataGenerationApp

This project is a group work by students at the Macromedia University of Applied Sciences. It's a Data Generation Application that allows users to generate and configure various types of data. The application is developed in Python 3 and is available as a Flask web application in the browser.


## How to Use
The programm redirects you trough 7 different sides. 
1. JsonUpload
you upload your pre made JSON Scheme.
2. Datensatz
You input the amount of data you want to generate and the filesize each generated file should have.
3. brokendata
you input the amount of broken data and the amount of empty data in % that you want in the end product.
if you dont want any broken data, input a 0 for both
4. Frequenz
Input the Minutes and Seconds by which you want to delay the upload
e.g. Minutes = 5, Seconds = 0, after each upload to your AWS S3 Cloud the programm is gonna wait 5 Minutes before uploading the next file
5. Distribution
Heres every datatype shown which had the value "int" within your JSON Scheme.
Select one of the following choices: Normal, Low, Mid, High, Low-Mid, Mid-High, Low-High.
Whenever the program generates an integer there will a 6 digits long number, dependend on what you have chosen before.
6. exampledownload
Shows you an example datapack, using the variables which you have chosen before.
if you are okay with the output press the Upload button which will start the downloading, and uploading process.
IMPORTANT: if you wish to delete the generated data after uploading you will find generated_data_* in your programm folder.
7. endscreen
Nothing else to input, simple feedback that the Process has finished and that there wont be any more uploads.


# Dockerfile

### Pull 

Pull `lisasmn/datagenapp` from the Docker repository:

    docker pull lisasmn/datagenapp

### Run

Run the image, binding associated ports, and mounting the present working
directory:

    docker run -d -p 5000:5000 lisasmn/datagenapp:latest


## Services

Service     | Port | Usage
------------|------|------
datagenapp  | 5000 | When using `datagenapp run`, visit `http://localhost:5000` in your browser


## Volumes

Volume          | Description
----------------|-------------
`/main.py`      | The location of the datagenapp application root.

## Authors

- [@JanGoedicke](https://github.com/JanGoedicke)
- [@iTzNoX](https://github.com/iTzNoX)
- [@bitterpeach](https://github.com/bitterpeach)
- [@ioana-vicol](https://github.com/ioana-vicol)
- Philipp Stepanow

