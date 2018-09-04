import argparse
import time
from os import path

from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges manually cleaned files back into a traced data file.")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to JSON input file, which contains a list of TracedData objects")
    parser.add_argument("coded_input_path", metavar="coded-input-path",
                        help="Directory to read manually-coded Coda files from")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write merged results to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    coded_input_path = args.coded_input_path
    json_output_path = args.json_output_path

    class MergePlan:
        def __init__(self, raw_field, coded_field, coda_name):
            self.raw_field = raw_field
            self.coded_field = coded_field
            self.coda_name = coda_name

    merge_plan = [
        MergePlan("district_review", "district", "District")
    ]

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Merge manually coded Coda files into the cleaned dataset
    for plan in merge_plan:
        coda_file_path = path.join(coded_input_path, "{}_coded.csv".format(plan.coda_name))

        if not path.exists(coda_file_path):
            print("Warning: No Coda file found for key '{}'".format(plan.coda_name))
            for td in surveys:
                td.append_data(
                    {plan.coded_field: None},
                    Metadata(user, Metadata.get_call_location(), time.time())
                )
            continue

        with open(coda_file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, surveys, plan.raw_field, {plan.coda_name: "{}_coded".format(plan.coded_field)}, f, True)

    # Write coded data back out to disk
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(surveys, f, pretty_print=True)
