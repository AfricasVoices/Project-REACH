import argparse

from core_data_modules.traced_data import TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO
from core_data_modules.util import IOUtils

from project_reach import CombineRawDatasets

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the post-fetch phase of the REACH pipeline")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("raw_messages_input_path", metavar="raw-messages-input-path",
                        help="Path to the input messages JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("raw_surveys_input_path", metavar="raw-surveys-input-path",
                        help="Path to the cleaned survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write TracedData for final analysis file to")

    args = parser.parse_args()
    user = args.user
    raw_messages_input_path = args.raw_messages_input_path
    raw_surveys_input_path = args.raw_surveys_input_path
    json_output_path = args.json_output_path

    # Load messages
    with open(raw_messages_input_path, "r") as f:
        messages = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Load surveys
    with open(raw_surveys_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Add survey data to the messages
    CombineRawDatasets.combine_raw_datasets(user, messages, surveys)

    # Write json output
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(messages, f, pretty_print=True)
