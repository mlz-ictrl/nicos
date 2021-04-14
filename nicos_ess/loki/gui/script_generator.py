from enum import Enum


class TransOrder(Enum):
    TRANSFIRST = 0
    SANSFIRST = 1
    TRANSTHENSANS = 2
    SANSTHENTRANS = 3
    SIMULTANEOUS = 4


class ScriptGenerator:
    def generate_script(
        self,
        labeled_data,
        trans_order,
        trans_duration_type,
        sans_duration_type):

        template = ""
        if trans_order == TransOrder.TRANSFIRST:
            for row_values in labeled_data:
                template += self._do_trans(row_values, trans_duration_type)

            for row_values in labeled_data:
                template += self._do_sans(row_values, sans_duration_type)
        elif trans_order == TransOrder.SANSFIRST:
            for row_values in labeled_data:
                template += self._do_sans(row_values, sans_duration_type)

            for row_values in labeled_data:
                template += self._do_trans(row_values, trans_duration_type)
        elif trans_order == TransOrder.TRANSTHENSANS:
            for row_values in labeled_data:
                template += self._do_trans(row_values, trans_duration_type)
                template += self._do_sans(row_values, sans_duration_type)

        elif trans_order == TransOrder.SANSTHENTRANS:
            for row_values in labeled_data:
                template += self._do_sans(row_values, sans_duration_type)
                template += self._do_trans(row_values, trans_duration_type)
        elif trans_order == TransOrder.SIMULTANEOUS:
            for row_values in labeled_data:
                template += self._do_sans(row_values, sans_duration_type)
        else:
            raise NotImplementedError(
                f"Unspecified trans order {trans_order.name}")

        return template

    def _do_trans(self, row_values, trans_duration_type):
        template = (
            f"{self._get_position(row_values['position'])}\n"
            f"{self._get_sample(row_values['sample'], row_values['thickness'])}\n"
            f"do_trans({row_values['trans_duration']}, "
            f"'{trans_duration_type}')\n")
        return template

    def _do_sans(self, row_values, sans_duration_type):
        template = (
            f"{self._get_position(row_values['position'])}\n"
            f"{self._get_sample(row_values['sample'], row_values['thickness'])}\n"
            f"do_sans({row_values['sans_duration']}, "
            f"'{sans_duration_type}')\n")
        return template

    def _get_position(self, value):
        return f"set_position({value})"

    def _get_sample(self, name, thickness):
        return f"set_sample('{name}', {thickness})"
