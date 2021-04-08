from enum import Enum


class TransOrder(Enum):
    TRANSFIRST = 0
    SANSFIRST = 1
    TRANSTHENSANS = 2
    SANSTHENTRANS = 3
    SIMULTANEOUS = 4


class ScriptGenerator:
    def generate_script(self, labeled_data, trans_order, trans_duration_type, sans_duration_type):
        template = ""
        if trans_order == TransOrder.TRANSFIRST:
            for row_values in labeled_data:
                template += self.do_trans(row_values, trans_duration_type)

            for row_values in labeled_data:
                template += self.do_sans(row_values, sans_duration_type)
        elif trans_order == TransOrder.SANSFIRST:
            for row_values in labeled_data:
                template += self.do_sans(row_values, sans_duration_type)

            for row_values in labeled_data:
                template += self.do_trans(row_values, trans_duration_type)
        elif trans_order == TransOrder.TRANSTHENSANS:
            for row_values in labeled_data:
                template += self.do_trans(row_values, trans_duration_type)
                template += self.do_sans(row_values, sans_duration_type)

        elif trans_order == TransOrder.SANSTHENTRANS:
            for row_values in labeled_data:
                template += self.do_sans(row_values, sans_duration_type)
                template += self.do_trans(row_values, trans_duration_type)
        elif trans_order == TransOrder.SIMULTANEOUS:
            pass
        else:
            assert True, "Unspecified trans order"
        return template

    def do_trans(self, row_values, trans_duration_type):
        template = (
            f"{self.get_position(row_values['position'])}\n"
            f"{self.get_sample(row_values['sample'], row_values['thickness'])}\n"
            f"do_trans({row_values['trans_duration']}, "
            f"'{trans_duration_type}')\n")
        return template

    def do_sans(self, row_values, sans_duration_type):
        template = (
            f"{self.get_position(row_values['position'])}\n"
            f"{self.get_sample(row_values['sample'], row_values['thickness'])}\n"
            f"do_sans({row_values['sans_duration']}, "
            f"'{sans_duration_type}')\n")
        return template

    def get_position(self, value):
        return f"set_position({value})"

    def get_sample(self, name, thickness):
        return f"set_sample('{name}', {thickness})"
