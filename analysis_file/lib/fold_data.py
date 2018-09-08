import time

from core_data_modules.traced_data import Metadata


class FoldData(object):
    # TODO: Move this class to Core Data?

    @staticmethod
    def group_by(data, collation_key_fn):
        collated_lut = dict()

        for td in data:
            key = collation_key_fn(td)
            if key not in collated_lut:
                collated_lut[key] = []
            collated_lut[key].append(td)

        return collated_lut.values()

    @staticmethod
    def process_grouped(collated_lists, collation_fn):
        collated = []
        for group in collated_lists:
            collated_td = group.pop(0)
            while len(group) > 0:
                collated_td = collation_fn(collated_td, group.pop(0))
            collated.append(collated_td)
        return collated

    @staticmethod
    def assert_equal_keys_equal(td_1, td_2, equal_keys):
        for key in equal_keys:
            assert td_1.get(key) == td_2.get(key), "Error: Key '{}' should be the same in both td_1 and td_2 but is " \
                                                   "different (has values '{}' and '{}' " \
                                                   "respectively)".format(key, td_1.get(key), td_2.get(key))

    @staticmethod
    def fold_concat_keys(user, td_1, td_2, concat_keys, concat_delimiter=";"):
        for key in concat_keys:
            concat_dict = dict()

            if key in td_1 and key in td_2:
                concat_dict[key] = "{}{}{}".format(td_1[key], concat_delimiter, td_2[key])

            td_1.append_data(concat_dict, Metadata(user, Metadata.get_call_location(), time.time()))
            td_2.append_data(concat_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def fold_matrix_keys(user, td_1, td_2, matrix_keys):
        matrix_dict = dict()
        for key in matrix_keys:
            matrix_values = {"0", "1"}

            if td_1.get(key) in matrix_values and td_2.get(key) in matrix_values:
                matrix_dict[key] = "1" if td_1.get(key) == "1" or td_2.get(key) == "1" else "0"
            elif td_1.get(key) in matrix_values:
                matrix_dict[key] = td_1[key]
            elif td_2.get(key) in matrix_values:
                matrix_dict[key] = td_2[key]
            else:
                matrix_dict[key] = None  # TODO: What should this really be?

        td_1.append_data(matrix_dict, Metadata(user, Metadata.get_call_location(), time.time()))
        td_2.append_data(matrix_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def set_other_keys_equal(user, td, other_keys):
        other_dict = dict()
        for key in other_keys:
            other_dict[key] = "MERGED"
        td.append_data(other_dict, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def fold_td(cls, user, td_1, td_2, equal_keys, concat_keys, matrix_keys, concat_delimiter=";"):
        cls.assert_equal_keys_equal(td_1, td_2, equal_keys)
        cls.fold_concat_keys(user, td_1, td_2, concat_keys, concat_delimiter)
        cls.fold_matrix_keys(user, td_1, td_2, matrix_keys)

        equal_keys = set(equal_keys)
        equal_keys.update(concat_keys)
        equal_keys.update(matrix_keys)

        cls.set_other_keys_equal(user, td_1, set(td_1.keys()) - set(equal_keys))
        cls.set_other_keys_equal(user, td_2, set(td_2.keys()) - set(equal_keys))

        collated_td = td_1.copy()
        collated_td.append_traced_data("collated_other", td_2, Metadata(user, Metadata.get_call_location(), time.time()))

        return collated_td

    @classmethod
    def fold(cls, user, data, collate_key_fn, equal_keys, concat_keys, matrix_keys, concat_delimiter=";"):
        return cls.process_grouped(
            FoldData.group_by(data, collate_key_fn),
            lambda td_1, td_2: cls.fold_td(user, td_1, td_2, equal_keys, concat_keys, matrix_keys, concat_delimiter)
        )
