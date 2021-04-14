from nicos.guisupport.qt import QAbstractTableModel, QModelIndex, Qt


class LokiScriptModel(QAbstractTableModel):
    def __init__(self, header_data, num_rows=25):
        super().__init__()

        self._header_data = header_data
        self._num_rows = num_rows
        self._table_data = self.empty_table(num_rows, len(header_data))

    @property
    def table_data(self):
        return self._table_data

    @table_data.setter
    def table_data(self, new_data):
        if not self._is_data_dimension_valid(new_data):
            raise AttributeError(
                f"Attribute must be a 2D list of shape (_, {len(self._header_data)})"
            )

        # Extend the list with empty rows if value has less than n_rows
        if len(new_data) < self._num_rows:
            new_data.extend(self.empty_table(
                    self._num_rows - len(new_data), len(self._header_data)))
        self._table_data = new_data
        self.layoutChanged.emit()

    def _is_data_dimension_valid(self, data):
        if not isinstance(data, list) and not all(
            [isinstance(val, list) and len(val) == len(self._header_data)
             for val in data]):
            return False
        return True

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._table_data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._table_data[index.row()][index.column()] = value
            return True

    def rowCount(self, index):
        return len(self._table_data)

    def columnCount(self, index):
        return len(self._table_data[0])

    def create_empty_row(self, position):
        self._table_data.insert(position, [''] * len(self._header_data))

    def update_data_at_index(self, row, column, value):
        self._table_data[row][column] = value
        self.layoutChanged.emit()

    def insertRow(self, position, index=QModelIndex()):
        self.beginInsertRows(index, position, position)
        self.create_empty_row(position)
        self.endInsertRows()
        return True

    def removeRows(self, rows, index=QModelIndex()):
        for row in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._table_data[row]
            self.endRemoveRows()
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._header_data[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return section + 1

    def setHeaderData(self, section, orientation, value, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            self._header_data[section] = value
            self.headerDataChanged.emit(orientation, section, section)
        return True

    def update_data_from_clipboard(
        self, copied_data, top_left_index, hidden_columns=None):
        # Copied data is tabular so insert at top-left most position
        for row_index, row_data in enumerate(copied_data):
            col_index = 0
            for value in row_data:
                if top_left_index[1] + col_index < len(self._table_data[0]):
                    current_column = top_left_index[1] + col_index
                    current_row = top_left_index[0] + row_index
                    col_index += 1
                    if current_row >= len(self._table_data):
                        self.create_empty_row(current_row)

                    if hidden_columns is not None and current_column in hidden_columns:
                        continue
                    self._table_data[current_row][current_column] = value

        self.layoutChanged.emit()

    def select_data(self, selected_indices):
        curr_row = -1
        row_data = []
        selected_data = []
        for row, column in selected_indices:
            if row != curr_row:
                if row_data:
                    selected_data.append('\t'.join(row_data))
                    row_data.clear()
            curr_row = row
            row_data.append(self._table_data[row][column])

        if row_data:
            selected_data.append('\t'.join(row_data))
            row_data.clear()
        return selected_data

    def clear(self):
        self.table_data = self.empty_table(
            len(self._table_data), len(self._header_data))

    def empty_table(self, rows, columns):
        return [[""] * columns for _ in range(rows)]
