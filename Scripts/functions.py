def read_file(filename: str) -> str:
    """
    Reads the content of a file and returns it as a string.
    
    Args:
        filename: Name of the file to read (without extension)
    
    Returns:
        The file content as a string
    """
    with open(f"../samples/{filename}.txt", 'r') as file:
        return file.read().strip()
