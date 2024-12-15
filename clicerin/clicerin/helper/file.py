def open_file(file: str):
    """
    Open and read a file, returning its contents.

    Args:
        file (str): The path to the file to be opened

    Returns:
        str: The contents of the file

    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there's an error reading the file
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file}") from e
    except IOError as e:
        raise IOError(f"Error reading file {file}: {str(e)}") from e
