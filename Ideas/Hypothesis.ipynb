import json
from hypothesis import strategies as st
from hypothesis import given, example


# Sample JSON schema
schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Alexa Analytics Event",
  "type": "object",
  "additionalProperties": "false",
  "properties": {
    "UserId": {
      "type": "string"
    },
    "Id": {
      "type": "string"
    },
    "SerialNumber": {
      "type": "string"
    },
    "payload": {
      "type": "object",
      "additionalProperties": "false",
      "properties": {
        "payloadType": {
          "type": "string",
          "enum": ["NOTIFICATION"],
          "default": "NOTIFICATION"
        },
        "analyticsCorrelationId": {
          "type": "string",
          "format": "uuid"
        },
        "homeApplianceType": {
          "type": "string",
          "enum": [
            "CLEANING_ROBOT",
            "COFFEEMAKER",
            "DISHWASHER",
            "DRYER",
            "HOOD",
            "OVEN",
            "REFRIGERATOR",
            "WASHER"
          ]
        },
        "timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "eventKey": {
          "type": "string"
        },
        "topic": {
          "type": "string"
        }
      },
      "title": "NOTIFICATION",
      "required": [
        "payloadType",
        "analyticsCorrelationId",
        "homeApplianceType",
        "timestamp",
        "eventKey",
        "topic"
      ]
    }
  },
  "required": ["UserId", "Id", "SerialNumber", "payload"]
}


def interpret_schema(schema):
    """
    Create a Hypothesis strategy based on a simplified interpretation of the JSON schema.
    Currently, this function is very basic and needs to be expanded to handle complex schemas.
    """
    properties = schema.get("properties", {})
    strategies = {}

    for prop, details in properties.items():
        if details["type"] == "string":
            strategies[prop] = st.text()
        elif details["type"] == "number":
            strategies[prop] = st.floats()
        elif details["type"] == "integer":
            strategies[prop] = st.integers()
        # Add more types as needed

    return st.fixed_dictionaries(strategies)


# Create a Hypothesis strategy from the schema
data_strategy = interpret_schema(schema)

# Use Hypothesis to generate an example
@example(data_strategy.example())
@given(data_strategy)
def test_generated_data(data):
    print(data)

test_generated_data()
