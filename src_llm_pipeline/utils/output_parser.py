import json
import textwrap
from typing import Dict, List

def parse_emotion_analysis(text: str, schema: Dict) -> Dict:
    """
    Parses the emotion analysis JSON string and enforces the schema's property ordering.

    Args:
        text: JSON string from LLM
        schema: Schema with property ordering information

    Returns:
        Dict: Parsed and reordered data matching schema ordering
    """
    data = json.loads(text)
    ordered_data = {}

    # Get root level ordering from schema
    root_ordering = schema.get("propertyOrdering", [])
    if not root_ordering:
        raise ValueError("Schema must define propertyOrdering")

    # Enforce root level ordering
    for key in root_ordering:
        if key in data:
            ordered_data[key] = {}
            sub_schema = schema["properties"].get(key, {})
            sub_ordering = sub_schema.get("propertyOrdering", [])

            # Enforce sub-level ordering
            if sub_ordering:
                for sub_key in sub_ordering:
                    if sub_key in data[key]:
                        ordered_data[key][sub_key] = data[key][sub_key]
                    else:
                        print(f"Warning: Expected property {sub_key} missing in {key}")

    # Validate that all required properties are present
    missing_props = [key for key in root_ordering if key not in ordered_data]
    if missing_props:
        raise ValueError(f"Missing required properties: {missing_props}")

    return ordered_data

def check_property_ordering(data: Dict, schema: Dict) -> bool:
    """
    Validates that the data strictly follows the schema's property ordering.

    Args:
        data: The parsed and ordered emotion analysis data
        schema: The schema with property ordering information

    Returns:
        bool: True if ordering matches exactly, False otherwise
    """
    # Check root level ordering
    root_ordering = schema.get("propertyOrdering", [])
    actual_root_keys = list(data.keys())

    if actual_root_keys != root_ordering:
        print("\nRoot level property ordering mismatch:")
        print(f"Expected: {root_ordering}")
        print(f"Actual: {actual_root_keys}")
        return False

    # Check sub-level ordering for each main section
    for section in root_ordering:
        if section in data and section in schema["properties"]:
            sub_schema = schema["properties"][section]
            sub_ordering = sub_schema.get("propertyOrdering", [])

            if sub_ordering:
                actual_sub_keys = list(data[section].keys())
                if actual_sub_keys != sub_ordering:
                    print(f"\nProperty ordering mismatch in {section}:")
                    print(f"Expected: {sub_ordering}")
                    print(f"Actual: {actual_sub_keys}")
                    return False

    return True

def print_emotion_analysis(data: Dict, width: int = 80):
    """
    Prints the emotion analysis data in a simplified format.

    Args:
        data: Parsed emotion analysis dictionary
        width: Maximum width for text wrapping
    """
    for section_name, section_content in data.items():
        print(f"\n{section_name.upper().replace('_', ' ')}")
        for key, value in section_content.items():
            print(f"{key.capitalize().replace('_', ' ')}:")
            print(textwrap.fill(str(value), width=width))
            print("---")