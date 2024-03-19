from rest_framework.metadata import SimpleMetadata


class METADATA_CHECK_EMAIL(SimpleMetadata):

    def determine_metadata(self, request, view):
        metadata = {
            "name": view.get_view_name(),
            "description": view.get_view_description(),
            "renders": ["application/json"],
            "parses": ["application/json"],
        }
        return metadata
