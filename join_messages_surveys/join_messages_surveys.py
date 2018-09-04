import argparse
import csv
import os
import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Joins radio show answers with survey answers on respondents' "
                                                 "phone ids.")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to the input messages JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("survey_input_path", metavar="survey-input-path",
                        help="Path to the cleaned survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("flow_name", metavar="flow-name",
                        help="Name of activation flow from which this data was derived")
    parser.add_argument("variable_name", metavar="variable-name",
                        help="Name of message variable in flow")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed messages to")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write the joined dataset to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    survey_input_path = args.survey_input_path
    variable_name = args.variable_name
    flow_name = args.flow_name
    json_output_path = args.json_output_path
    csv_output_path = args.csv_output_path

    # Load messages
    with open(json_input_path, "r") as f:
        messages = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Add survey data to the messages
    TracedData.update_iterable(user, "avf_phone_id", data, surveys, "survey_responses")

    TracedData.update_iterable(user, "avf_phone_id", messages, surveys, "survey_responses")

    # Write json output
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(messages, f, pretty_print=True)

    with open(csv_output_path, "w") as f:
        f.write("{}")
