import sys
import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCSVIO
from core_data_modules.traced_data.util import FoldTracedData
from core_data_modules.util.consent_utils import ConsentUtils

from project_reach.lib.analysis_keys import AnalysisKeys


class AnalysisFile(object):
    @staticmethod
    def generate(user, data, csv_by_message_output_path, csv_by_individual_output_path):
        # Serializer is currently overflowing
        # TODO: Investigate/address the cause of this.
        sys.setrecursionlimit(10000)

        demog_keys = [
            "district",
            "region",
            "state",
            "zone",
            "district_coda",
            "district_raw",
            "gender",
            "gender_raw",
            "urban_rural",
            "urban_rural_raw",
            "age",
            "age_raw",
            "assessment",
            "assessment_raw",
            "idp",
            "idp_raw"
        ]

        evaluation_keys = [
            "involved",
            "involved_raw",
            "repeated",
            "repeated_raw"
        ]

        rapid_pro_consent_withdrawn_key = "esc4jmcna_consent_s07e01_complete"
        avf_consent_withdrawn_key = "withdrawn_consent"

        # Translate keys to final values for analysis
        show_keys = set()  # of all radio show matrix keys
        AnalysisKeys.set_analysis_keys(user, data, {
            "UID": "avf_phone_id",
            "operator": "operator",
            "humanitarian_priorities_raw": "S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation",

            "gender": "gender_coded",
            "gender_raw": "gender_review",

            "district": "district_coded",
            "region": "region_coded",
            "state": "state_coded",
            "zone": "zone_coded",
            "district_raw": "district_review",

            "urban_rural": "urban_rural_coded",
            "urban_rural_raw": "urban_rural_review",

            "age": "age_coded",
            "age_raw": "age_review",

            "assessment": "assessment_coded",
            "assessment_raw": "assessment_review",

            "idp": "idp_coded",
            "idp_raw": "idp_review",

            "involved": "involved_esc4jmcna_coded",
            "involved_raw": "involved_esc4jmcna",

            "repeated": "repeated_esc4jmcna_coded",
            "repeated_raw": "repeated_esc4jmcna"
        })

        AnalysisKeys.set_matrix_keys(
            user, data, show_keys, "S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation_coded",
            "humanitarian_priorities"
        )

        show_keys = list(show_keys)
        show_keys.sort()

        equal_keys = ["UID", "operator"]
        equal_keys.extend(demog_keys)
        equal_keys.extend(evaluation_keys)
        concat_keys = ["humanitarian_priorities_raw"]
        matrix_keys = show_keys
        bool_keys = [
            avf_consent_withdrawn_key,

            "bulk_sms",
            "sms_ad",
            "radio_promo",
            "radio_show",
            "non_logical_time"
        ]

        # Export to CSV
        export_keys = ["UID", "operator"]
        export_keys.extend(bool_keys)
        export_keys.extend(show_keys)
        export_keys.append("humanitarian_priorities_raw")
        export_keys.extend(demog_keys)
        export_keys.extend(evaluation_keys)

        # Set consent withdrawn based on presence of data coded as "stop"
        ConsentUtils.determine_consent_withdrawn(user, data, export_keys, avf_consent_withdrawn_key)

        # Set consent withdrawn based on stop codes from humanitarian priorities.
        # TODO: Update Core Data to set 'stop's instead of '1's?
        for td in data:
            if td.get("humanitarian_priorities_stop") == "1":
                td.append_data({avf_consent_withdrawn_key: Codes.TRUE},
                               Metadata(user, Metadata.get_call_location(), time.time()))

        # Set consent withdrawn based on auto-categorisation in Rapid Pro
        for td in data:
            if td.get(rapid_pro_consent_withdrawn_key) == "yes":  # Not using Codes.YES because this is from Rapid Pro
                td.append_data({avf_consent_withdrawn_key: Codes.TRUE},
                               Metadata(user, Metadata.get_call_location(), time.time()))

        for td in data:
            if avf_consent_withdrawn_key not in td:
                td.append_data({avf_consent_withdrawn_key: Codes.FALSE},
                               Metadata(user, Metadata.get_call_location(), time.time()))

        # Fold data to have one respondent per row
        to_be_folded = []
        for td in data:
            to_be_folded.append(td.copy())

        folded_data = FoldTracedData.fold_iterable_of_traced_data(
            user, data, fold_id_fn=lambda td: td["UID"],
            equal_keys=equal_keys, concat_keys=concat_keys, matrix_keys=matrix_keys, bool_keys=bool_keys
        )

        # Process consent
        ConsentUtils.set_stopped(user, data, avf_consent_withdrawn_key)
        ConsentUtils.set_stopped(user, folded_data, avf_consent_withdrawn_key)

        # Output to CSV with one message per row
        with open(csv_by_message_output_path, "w") as f:
            TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)

        with open(csv_by_individual_output_path, "w") as f:
            TracedDataCSVIO.export_traced_data_iterable_to_csv(folded_data, f, headers=export_keys)

        return data
