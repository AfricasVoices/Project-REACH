import time

import pytz  # Timezone library for converting datetime objects between timezones
from core_data_modules.cleaners import Codes, somali
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

        stopped = td.get("{}_{}".format(coded_shows_prefix, Codes.STOP)) == "1"

        for output_key in td:
            if output_key.startswith(coded_shows_prefix):
                code_key = output_key.replace(coded_shows_prefix, radio_q_prefix)

                if code_key.endswith(Codes.STOP):
                    continue

                show_keys.add(code_key)
                if stopped:
                    matrix_d[code_key] = Codes.STOP
                else:
                    matrix_d[code_key] = td[output_key]

        td.append_data(matrix_d, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def set_analysis_keys(cls, user, td):
        # Set district/region/state/zone codes from the coded district field.
        # TODO: Move elsewhere
        if not somali.DemographicCleaner.is_location(td["district_coded"]) and td["district_coded"] != "other" and \
                td["district_coded"] != "NC" and td["district_coded"] is not None:
            print("Unknown district: '{}'".format(td["district_coded"]))

        def convert_nc(value):
            if value == Codes.NOT_CODED:
                return "NC"
            return value

        td.append_data({
            "district_coded": convert_nc(somali.DemographicCleaner.get_district(td["district_coded"])),
            "region_coded": convert_nc(somali.DemographicCleaner.get_region(td["district_coded"])),
            "state_coded": convert_nc(somali.DemographicCleaner.get_state(td["district_coded"])),
            "zone_coded": convert_nc(somali.DemographicCleaner.get_zone(td["district_coded"])),
            "district_coded_no_hierarchy": td["district_coded"]
        }, Metadata(user, Metadata.get_call_location(), time.time()))

        td.append_data({
            "UID": td["avf_phone_id"],
            "operator": td["operator"],
            "humanitarian_priorities_raw": td["S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation"],

            "gender": cls.get_code(td, "gender_review", "gender_coded"),
            "gender_raw": td.get("gender_review", Codes.TRUE_MISSING),

            "district": cls.get_code(td, "district_review", "district_coded"),
            # In the items below, use district_review as the raw field because this is the field these are all
            # derived from.
            "region": cls.get_code(td, "district_review", "region_coded"),
            "state": cls.get_code(td, "district_review", "state_coded"),
            "zone": cls.get_code(td, "district_review", "zone_coded"),
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
            "repeated_raw": td.get("repeated_esc4jmcna", Codes.TRUE_MISSING),
        }, Metadata(user, Metadata.get_call_location(), time.time()))
