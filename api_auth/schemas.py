from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import ParseError
import jsonschema


class CustomJSONParser(JSONParser):
    user_create_request_schema = {
        "title": "CustomUser",
        "type": "object",
        "properties": {
            "password1": {"type": "string"},
            "password2": {"type": "string"},
            "username": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "user_type": {
                "type": "string",
                "enum": [
                    "CUSTOMER",
                    "SELLER",
                    "CUSTOMER REPRESENTATIVE",
                    "MANAGER",
                    "ADMINISTRATOR",
                ],
            },
            "image": {"type": "string"},
            "user_google_id": {"type": "integer"},
        },
        "required": ["password1", "password2", "username", "email", "user_type"],
    }

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as JSON, returning the data
        """
        # Call the parent class' parse method to obtain JSON data
        data = super().parse(stream, media_type, parser_context)

        # Validate JSON data against the schema
        try:
            jsonschema.validate(data, self.user_create_request_schema)
        except jsonschema.ValidationError as e:
            raise ParseError(detail=str(e))

        except jsonschema.SchemaError as e:
            raise ParseError(detail=str(e))

        return data


class CustomJSONRenderer(JSONRenderer):
    user_create_response_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "user_type": {
                "type": "string",
                "enum": [
                    "CUSTOMER",
                    "SELLER",
                    "CUSTOMER REPRESENTATIVE",
                    "MANAGER",
                    "ADMINISTRATOR",
                ],
            },
            "image": {"type": "string"},
            "user_google_id": {"type": "integer"},
        },
        "required": ["username", "email", "user_type"],
    }

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Call the parent class' render method to obtain the rendered JSON data
        rendered_data = super().render(data, accepted_media_type, renderer_context)

        # Validate the rendered JSON data against the schema
        try:
            jsonschema.validate(data, self.user_create_response_schema)
        except jsonschema.ValidationError as e:
            # If validation fails, raise a ValidationError
            raise jsonschema.ValidationError(detail=str(e))
        except jsonschema.SchemaError as e:
            # If schema error occurs, raise a SchemaError
            raise jsonschema.SchemaError(detail=str(e))

        return rendered_data
