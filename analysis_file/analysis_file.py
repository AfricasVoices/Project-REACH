import argparse
import sys
import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.traced_data.util import FoldTracedData

from lib.analysis_keys import AnalysisKeys
from lib.consent import Consent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates files for analysis from the cleaned and coded show "
                                                 "and survey responses")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("messages_input_dir", metavar="messages-input-dir",
                        help="Path to a directory containing JSON files of responses to each of the shows in this "
                             "project. Each JSON file should contain a list of serialized TracedData objects")
    parser.add_argument("survey_input_path", metavar="survey-input-path",
                        help="Path to a coded survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write serialized TracedData items to after modification by this"
                             "pipeline stage")
    parser.add_argument("csv_by_message_output_path", metavar="csv-by-message-output-path",
                        help="Analysis dataset where messages are the unit for analysis (i.e. one message per row)")
    parser.add_argument("csv_by_individual_output_path", metavar="csv-by-individual-output-path",
                        help="Analysis dataset where respondents are the unit for analysis (i.e. one respondent "
                             "per row, with all their messages joined into a single cell).")

    args = parser.parse_args()
    user = args.user
    data_input_path = args.survey_input_path
    json_output_path = args.json_output_path
    csv_by_message_output_path = args.csv_by_message_output_path
    csv_by_individual_output_path = args.csv_by_individual_output_path

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

    # Load cleaned and coded message/survey data
    with open(data_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Translate keys to final values for analysis
    show_keys = set()
    for td in data:
        AnalysisKeys.set_analysis_keys(user, td)
        AnalysisKeys.set_matrix_keys(
            user, td, show_keys, "S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation_coded",
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
        "withdrawn_consent",

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
    Consent.determine_consent(user, data, export_keys)

    # Set consent withdrawn based on stop codes from humanitarian priorities.
    # TODO: Update Core Data to set 'stop's instead of '1's?
    for td in data:
        if td.get("humanitarian_priorities_stop") == "1":
            td.append_data({"withdrawn_consent": Codes.TRUE}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Set consent withdrawn based on auto-categorisation in Rapid Pro
    for td in data:
        if td.get(rapid_pro_consent_withdrawn_key) == "yes":  # Not using Codes.YES because this is from Rapid Pro
            td.append_data({"withdrawn_consent": Codes.TRUE}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Fold data to have one respondent per row
    to_be_folded = []
    for td in data:
        to_be_folded.append(td.copy())

    folded_data = FoldTracedData.fold_iterable_of_traced_data(
        user, data, fold_id_fn=lambda td: td["UID"],
        equal_keys=equal_keys, concat_keys=concat_keys, matrix_keys=matrix_keys, bool_keys=bool_keys
    )

    # Process consent.
    # TODO: This split between determine_consent and set_stopped is weird.
    # TODO: Fix this by re-engineering FoldData to cope with consent directly?
    stop_keys = set(export_keys) - {"withdrawn_consent"}
    Consent.set_stopped(user, data, stop_keys)
    Consent.set_stopped(user, folded_data, stop_keys)

    # Output to CSV with one message per row
    with open(csv_by_message_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)

    with open(csv_by_individual_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(folded_data, f, headers=export_keys)

    # Export JSON
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(folded_data, f, pretty_print=True)
