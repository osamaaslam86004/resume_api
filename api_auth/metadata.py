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
