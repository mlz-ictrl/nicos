import csv


def save_table_to_csv(data, filename, headers=None):
    """Save 2D data list to a text file.

    :param data: 2D data list
    :param filename: file to save as
    :param headers: List of column names.
    """
    with open(filename, "w") as file:
        writer = csv.writer(file)
        if headers:
            writer.writerow(headers)
        writer.writerows(data)


def load_table_from_csv(filename):
    """Load data for from a csv file.

    Note: May contain headers

    :param filename: path to csv file
    :return: 2D data list
    """
    with open(filename, "r") as file:
        reader = csv.reader(file)
        data = [row for row in reader]

    return data
