from rest_framework.parsers import MultiPartParser


class MultiPartWithNestedToDictParser(MultiPartParser):
    """
    Parses multipart/form-data structures with key conventions:
      - Double underscore "__" denotes nesting
      - Suffix "[]" denotes list fields

    Example request load:
        about__smoking_level = 2
        about__other_animals[] = cat
        about__other_animals[] = dog
        rent_preferences__locations[] = kyiv

    Output JSON-like structure:
        {
            "about": {
                "smoking_level": "2",
                "other_animals": ["cat", "dog"]
            },
            "rent_preferences": {
                "locations": ["kyiv"]
            }
        }

    It does not assume types for literals - do it in a controlled way in the serializer to avoid bugs like name=True
    """

    def parse(self, stream, media_type=None, parser_context=None):
        basic_result = super().parse(stream, media_type, parser_context)
        jsonified_data = self._jsonify_data(basic_result)
        return jsonified_data

    def _jsonify_data(self, data):
        """Convert flat QueryDict (all values come from parent Parser as lists) to a nested JSON with correct types."""
        all_data_lists = list(data.data.lists()) + list(data.files.lists())
        jsonified_data: dict = {}

        for key_schema, field_value_as_list in all_data_lists:
            # scan the key structure
            is_list_field = key_schema.endswith("[]")
            if is_list_field:
                key_schema = key_schema[:-2]  # remove []

            key_nodes = key_schema.split("__")  # split nested key
            fieldgroup_keys = key_nodes[:-1]  # where to nest
            field_key = key_nodes[-1]  # what to nest
            current_fieldgroup = jsonified_data  # current nested level

            # set nested structure {stuff: {about: {etc...}}}
            for key in fieldgroup_keys:
                if key not in current_fieldgroup:
                    current_fieldgroup[key] = {}
                current_fieldgroup = current_fieldgroup[key]  # go level deeper

            # get value as list or literal
            field_value_raw = field_value_as_list if is_list_field else field_value_as_list[0]

            # interpret [''] -> as empty list []
            if is_list_field and field_value_raw == ['']:
                field_value_raw = []

            # set final value
            current_fieldgroup[field_key] = field_value_raw

        return jsonified_data


class UnexpectedFieldError(ValueError):
    pass


def validate_received_data_structure(received_data, serializer):
    def _recusrion(_received_data, _expected_fields, prev=None):
        for key, value in _received_data.items():
            if key not in _expected_fields:
                raise UnexpectedFieldError(
                    f"""Unexpected field '{f"{prev}__{key}" if prev else key}' in received data""")

            # Check if the value is a dictionary (nested structure)
            if isinstance(value, dict):
                _recusrion(value, _expected_fields[key], prev=key)

    expected_fields = serializer(data={}).get_fields()
    _recusrion(received_data, expected_fields)
