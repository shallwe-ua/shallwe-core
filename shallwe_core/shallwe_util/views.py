from rest_framework.parsers import MultiPartParser


class MultiPartWithNestedToJSONParser(MultiPartParser):
    """
    Parses structures like\n
    {
        block1[param1]: value1,\n
        block1[param2]: value2,\n
        block2: [1, 2, 3]
    }\n
    Into JSON-like\n
    {
        block1: {
            param1: value1,\n
            param2: value2\n
        },
        block2: [1, 2, 3]
    }\n
    Also returns all data as data, doesn't use file attribute as it's not used in serializers
    """

    def _jsonify_data(self, data):
        all_data_lists = list(data.data.lists()) + list(data.files.lists())
        jsonified_data = {}
        for key, value in all_data_lists:
            parts = key.split('[')
            current = jsonified_data
            for part in parts[:-1]:
                part_name = part.rstrip(']')
                if part_name not in current:
                    current[part_name] = {}
                current = current[part_name]
            final_key = parts[-1].rstrip(']')
            # Convert value to int, list of ints, boolean, or list of booleans if possible
            final_value = self._convert_value(value)
            current[final_key] = final_value
        return jsonified_data

    def _convert_value(self, value):
        # Check if value is a list
        if isinstance(value, list):
            # If list has only one item, return the item directly
            if len(value) == 1:
                return self._convert_value(value[0])
            # Recursively process each item in the list
            return [self._convert_value(item) for item in value]
        # Convert value to int if possible
        elif isinstance(value, str) and value.isdigit():
            return int(value)
        # Convert to boolean if possible
        elif isinstance(value, str) and value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        else:
            return value

    def parse(self, stream, media_type=None, parser_context=None):
        basic_result = super().parse(stream, media_type, parser_context)
        jsonified_data = self._jsonify_data(basic_result)
        return jsonified_data


class UnexpectedFieldError(ValueError):
    pass


def validate_received_data_structure(received_data, serializer):
    def _recusrion(_received_data, _expected_fields, prev=None):
        for key, value in _received_data.items():
            if key not in _expected_fields:
                raise UnexpectedFieldError(
                    f"""Unexpected field '{f"{prev}[{key}]" if prev else key}' in received data""")

            # Check if the value is a dictionary (nested structure)
            if isinstance(value, dict):
                _recusrion(value, _expected_fields[key], prev=key)

    expected_fields = serializer(data={}).get_fields()
    _recusrion(received_data, expected_fields)
