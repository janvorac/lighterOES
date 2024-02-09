import pandas as pd


class ReadDataError(Exception):
    pass


def read_data(filename):
    """Reads data from a file and returns a pandas DataFrame.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        pandas.DataFrame: The data read from the file.
    """
    try:
        data = pd.read_csv(filename, index_col=0)
    except Exception as e:
        raise ReadDataError(f"Error reading data from {filename}") from e
    return data
