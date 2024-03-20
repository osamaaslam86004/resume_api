from rest_framework.metadata import SimpleMetadata


class METADATA_JSON_PARSES_JSON_RENDERS(SimpleMetadata):

    def determine_metadata(self, request, view):
        metadata = {
            "name": view.get_view_name(),
            "description": view.get_view_description(),
            "renders": ["application/json"],
            "parses": ["application/json"],
        }
        return metadata


class PasswordResetMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)

        if hasattr(view, "OutputSerializer") and view.OutputSerializer:
            serializer = view.OutputSerializer()
            metadata["schema"] = self.get_serializer_schema(serializer)

        return metadata

    def get_serializer_schema(self, serializer):
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for field_name, field in serializer.fields.items():
            schema["properties"][field_name] = self.get_field_schema(field)
            if getattr(field, "required", False):
                schema["required"].append(field_name)

        return schema

    def get_field_schema(self, field):
        field_schema = {"type": field.__class__.__name__}
        return field_schema
