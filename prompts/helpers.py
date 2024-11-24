def format_filename(file_path):
    """Extracts filename from file path"""
    split_path = file_path.split("/")
    return split_path[-1]
