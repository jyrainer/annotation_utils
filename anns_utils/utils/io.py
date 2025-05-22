import json

def load_json(file_path):
    """
    Loads JSON data from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Loaded JSON data.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_json(data, file_path):
    """
    Saves JSON data to a file.

    Args:
        data (dict): JSON data to be saved.
        file_path (str): Path to save the JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(data, f)
        
