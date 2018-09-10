import time

import pytz
from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from dateutil.parser import isoparse


class AnalysisKeys(object):
    # TODO: Move some of these methods to Core Data?

    @staticmethod
    def get_code(td, key_of_raw, key_of_coded=None):
        """
        Returns the coded value for a response if one was provided, otherwise returns Codes.TRUE_MISSING

        :param td: TracedData item to return the coded value of
        :type td: TracedData
        :param key_of_raw: Key in td of the raw response
        :type key_of_raw: str
        :param key_of_coded: Key in td of the coded response. Defaults to '<key_of_raw>_coded' if None
        :type key_of_coded: str
        :return: The coded value for a response if one was provided, otherwise Codes.TRUE_MISSING
        :rtype: str
        """
        if key_of_coded is None:
            key_of_coded = "{}_coded".format(key_of_raw)

        if td[key_of_raw] == Codes.TRUE_MISSING:
            return Codes.TRUE_MISSING
        else:
            return td[key_of_coded]

    @staticmethod
    def get_date_time_utc(td):
        return isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_date_time_eat(td):
        return isoparse(td["created_on"]).astimezone(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def set_yes_no_matrix_keys(user, td, show_keys, coded_shows_prefix, radio_q_prefix):
        matrix_d = dict()

        yes_no_key = coded_shows_prefix + "_yes_no"
        yes_no = td[yes_no_key]
        matrix_d[radio_q_prefix] = yes_no

        for key in td:
            if key.startswith(coded_shows_prefix) and key != yes_no_key:
                yes_prefix = radio_q_prefix + "_yes"
                no_prefix = radio_q_prefix + "_no"

                code_yes_key = key.replace(coded_shows_prefix, yes_prefix)
                code_no_key = key.replace(coded_shows_prefix, no_prefix)
                show_keys.update({code_yes_key, code_no_key})

                matrix_d[code_yes_key] = td[key] if yes_no == Codes.YES else "0"
                matrix_d[code_no_key] = td[key] if yes_no == Codes.NO else "0"

        td.append_data(matrix_d, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def set_matrix_keys(user, td, show_keys, coded_shows_prefix, radio_q_prefix):
        matrix_d = dict()

        special = None
        if td.get("{}_NC".format(coded_shows_prefix)) == "1":  # TODO: Change to use Codes.NOT_CODED
            special = "0"
        if td.get("{}_stop".format(coded_shows_prefix)) == "1":  # TODO: Change to use Codes.STOP?
            special = "stop"

        for output_key in td:
            if output_key.startswith(coded_shows_prefix):
                code_key = output_key.replace(coded_shows_prefix, radio_q_prefix)

                if code_key.endswith("_NC") or code_key.endswith("_stop"):  # TODO: Change to use Codes
                    continue

                show_keys.add(code_key)
                if special is not None:
                    matrix_d[code_key] = special
                else:
                    matrix_d[code_key] = td[output_key]

        td.append_data(matrix_d, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def set_analysis_keys(cls, user, td):
        td.append_data({
            "UID": td["avf_phone_id"],
            "humanitarian_priorities_raw": td["S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation"],

            "gender": cls.get_code(td, "gender_review", "gender_coded"),
            "gender_raw": td.get("gender_review", Codes.TRUE_MISSING),

            "district": cls.get_code(td, "district_review", "district_coded"),
            "district_raw": td.get("district_review", Codes.TRUE_MISSING),

            "urban_rural": cls.get_code(td, "urban_rural_review", "urban_rural_coded"),
            "urban_rural_raw": td.get("urban_rural_review", Codes.TRUE_MISSING),

            "age": cls.get_code(td, "age_review", "age_coded"),
            "age_raw": td.get("age_review", Codes.TRUE_MISSING),

            "assessment": cls.get_code(td, "assessment_review", "assessment_coded"),
            "assessment_raw": td.get("assessment_review", Codes.TRUE_MISSING),

            "idp": cls.get_code(td, "idp_review", "idp_coded"),
            "idp_raw": td.get("idp_review", Codes.TRUE_MISSING),

            "involved": cls.get_code(td, "involved_esc4jmcna", "involved_esc4jmcna_coded"),
            "involved_raw": td.get("involved_esc4jmcna", Codes.TRUE_MISSING),

            "repeated": cls.get_code(td, "repeated_esc4jmcna", "repeated_esc4jmcna_coded"),
            "repeated_raw": td.get("repeated_esc4jmcna", Codes.TRUE_MISSING)
        }, Metadata(user, Metadata.get_call_location(), time.time()))
