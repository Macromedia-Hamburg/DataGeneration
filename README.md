
# DataGenerationApp

This project is a group work by students at Macromedia Hamburg. it is a Data Generation Application that allows users to generate and configure various types of data. The application is developed in Python 3 and is available as a Flask web application in the browser.




## Authors

- [@JanGoedicke](https://github.com/JanGoedicke)
- [@iTzNoX](https://github.com/iTzNoX)
- [@bitterpeach](https://github.com/bitterpeach)
- [@ioana-vicol](https://github.com/ioana-vicol)
- philipp

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



