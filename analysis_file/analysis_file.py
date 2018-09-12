import argparse
import sys

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO

from lib.analysis_keys import AnalysisKeys
from lib.fold_data import FoldData

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

    demog_keys = [
        "district",
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

    group_by_fn = lambda td: td["avf_phone_id"]
    equal_keys = ["UID", "operator"]
    equal_keys.extend(demog_keys)
    equal_keys.extend(evaluation_keys)
    concat_keys = ["humanitarian_priorities_raw"]
    matrix_keys = show_keys

    # TODO: Output data before folding.

    # Fold data such that we get one TracedData item in data per individual.
    data = FoldData.fold(user, data, group_by_fn, equal_keys, concat_keys, matrix_keys)

    # Export to CSV
    export_keys = ["UID", "operator"]
    export_keys.extend(show_keys)
    export_keys.append("humanitarian_priorities_raw")
    export_keys.extend(demog_keys)
    export_keys.extend(evaluation_keys)

    # TODO: Output data before folding.

    # Output to CSV with one message per row
    with open(csv_by_message_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)

    sys.setrecursionlimit(1500)

    # Export to CSV with one respondent per row
    data = FoldData.fold(user, data, group_by_fn, equal_keys, concat_keys, matrix_keys)
    with open(csv_by_individual_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)

    # Export JSON
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)
