import csv

from nicos.guisupport.qt import QTableWidgetItem


def save_table_to_csv(table, filename, headers=None):
    """Save QTableWidget data to a text file

    Parameters:
    -----------
        table (QTableWidget): Table widget to be saved
        filename (str): path to the filename
        headers (List[str], optional): List of column names.
            Defaults to None. If None, it will use the horizontalHeaderItem
            from QTableWidget
    """
    with open(filename, "w") as file:
        headers_to_write = []
        data = []
        writer = csv.writer(file)
        for column in range(table.columnCount()):
            if not table.isColumnHidden(column):
                header = (
                    headers[column] if headers else table.horizontalHeaderItem(column)
                )
                headers_to_write.append(header.replace("\n", ""))

        writer.writerow(headers_to_write)

        for row in range(table.rowCount()):
            rowdata = []
            for column in range(table.columnCount()):
                if not table.isColumnHidden(column):
                    item = table.item(row, column)
                    if item is not None:
                        rowdata.append(item.text())
                    else:
                        rowdata.append("")
            if any(rowdata):
                data.append(rowdata)
        writer.writerows(data)


def load_table_from_csv(table, headers, filename):
    """Load QTableWidget data for from a text file
       Allows to load partial table from filename.

    Parameters:
    -----------
        table (QTableWidget): Table widget to be loaded
        headers (List[str]): List of column names in table.
            len(headers) must be same as number of columns in table
        filename (str): Path to the filename

    Raises:
    -------
        ValueError

    Returns:
    --------
        headers_from_file (List(str)): List of headers read from filename
    """

    def _update_cell(row, column, value, table=table):
        item = table.item(row, column)
        if not item:
            table.setItem(row, column, QTableWidgetItem(value))
        else:
            item.setText(value)

    if len(headers) != table.columnCount():
        raise ValueError(
            f"Length of headers {len(headers)} does not match"
            f"the number of colums {table.columnCount()} in table"
        )

    with open(filename, "r") as file:
        reader = csv.reader(file)
        headers_from_file = next(reader)

        # If headers were modified by hand in the file by user
        if not set(headers_from_file).issubset(set(headers)):
            raise ValueError(
                f"Headers in {filename} are not correct \n",
                f"Available headers {headers}",
            )

        # clear existing entries in table
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                _update_cell(row, column, "")

        # corresponding indices of elements in headers_read list to headers
        indices = [i for i, e in enumerate(headers) if e in headers_from_file]
        ncols = len(headers)

        for row, data in enumerate(reader):
            # create appropriate length list to fill the table row
            data = _fill_elements(data, indices, ncols)
            for column in range(table.columnCount()):
                _update_cell(row, column, data[column])

    return headers_from_file


def _fill_elements(row, indices, length):
    """Returns a list of len length, with elements of row placed at
    given indices.
    """
    if len(row) == length:
        return row
    r = [""] * length
    # Slicing similar to numpy arrays r[indices] = row
    for index, value in zip(indices, row):
        r[index] = value
    return r
