import argparse
import time
from os import path

from core_data_modules.cleaners import CharacterCleaner, Codes, somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO, TracedDataTheInterfaceIO
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
    parser.add_argument("interface_output_dir", metavar="interface-output-dir",
                        help="Path to a directory to write The Interface files to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    coded_input_path = args.coded_input_path
    json_output_path = args.json_output_path
    interface_output_dir = args.interface_output_dir

    class MergePlan:
        def __init__(self, raw_field, coded_field, coda_name):
            self.raw_field = raw_field
            self.coded_field = coded_field
            self.coda_name = coda_name

    merge_plan = [
        MergePlan("gender_review", "gender_coded", "Gender"),
        MergePlan("district_review", "district_coded", "District"),
        MergePlan("urban_rural_review", "urban_rural_coded", "Urban_Rural"),
        MergePlan("age_review", "age_coded", "Age"),
        MergePlan("assessment_review", "assessment_coded", "Assessment"),
        MergePlan("idp_review", "idp_coded", "IDP"),

        MergePlan("involved_esc4jmcna", "involved_esc4jmcna_coded", "Involved"),
        MergePlan("repeated_esc4jmcna", "repeated_esc4jmcna_coded", "Repeated")
    ]

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Merge manually coded survey/evaluation Coda files into the cleaned dataset
    for plan in merge_plan:
        coda_file_path = path.join(coded_input_path, "{}_coded.csv".format(plan.coda_name))

        if not path.exists(coda_file_path):
            print("Warning: No Coda file found for key '{}'".format(plan.coda_name))
            for td in data:
                td.append_data(
                    {plan.coded_field: None},
                    Metadata(user, Metadata.get_call_location(), time.time())
                )
            continue

        with open(coda_file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, data, plan.raw_field, {plan.coda_name: plan.coded_field}, f, True)

    # Set districts coded as 'other' to 'NC'
    for td in data:
        if td["district_coded"] == "other":
            td.append_data({"district_coded": "NC"}, Metadata(user, Metadata.get_call_location(), time.time()))

    def convert_nc(value):
        if value == Codes.NOT_CODED:
            return "NC"
        return value

    # Set district/region/state/zone codes from the coded district field.
    for td in data:
        if not somali.DemographicCleaner.is_location_code(td["district_coded"]) and \
                td["district_coded"] != Codes.STOP and \
                td["district_coded"] != "NC" and td["district_coded"] is not None:
            print("Unknown district: '{}'".format(td["district_coded"]))

        td.append_data({
            "district_coded": convert_nc(somali.DemographicCleaner.district_for_location_code(td["district_coded"])),
            "region_coded": convert_nc(somali.DemographicCleaner.region_for_location_code(td["district_coded"])),
            "state_coded": convert_nc(somali.DemographicCleaner.state_for_location_code(td["district_coded"])),
            "zone_coded": convert_nc(somali.DemographicCleaner.zone_for_location_code(td["district_coded"])),
            "district_coda": Codes.TRUE_MISSING if td["district_review"] == Codes.TRUE_MISSING else td["district_coded"]
        }, Metadata(user, Metadata.get_call_location(), time.time()))

        # If we failed to find a zone after searching location codes, try inferring from the operator code instead
        if td["zone_coded"] == "NC":
            td.append_data({
                "zone_coded": convert_nc(somali.DemographicCleaner.zone_for_operator_code(td["operator"]))
            }, Metadata(user, Metadata.get_call_location(), time.time()))

    # Merge manually coded activation Coda files into the cleaned dataset
    coda_file_path = path.join(coded_input_path, "esc4jmcna_activation_coded.csv")
    key_of_raw = "S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation"
    key_of_coded_prefix = "{}_coded_".format(key_of_raw)
    key_of_coded_relevance = "{}_relevance_coded".format(key_of_raw)
    if path.exists(coda_file_path):
        with open(coda_file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable_as_matrix(
                user, data, key_of_raw, {"Code 1", "Code 2", "Code 3", "Code 4", "Code 5"}, f, key_of_coded_prefix)

        with open(coda_file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, data, key_of_raw, {"Relevance": key_of_coded_relevance}, f)

    # Fix Not Reviewed to account for data which had relevant set only, to work around a Coda bug
    key_of_coded_nr = "{}{}".format(key_of_coded_prefix, Codes.NOT_REVIEWED)
    for td in data:
        if td.get(key_of_coded_relevance) is not None:
            td.append_data({key_of_coded_nr: "0"}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Assume everything that wasn't reviewed should have been assigned NOT_CODED, to work around a Coda bug
    key_of_coded_nc = "{}NC".format(key_of_coded_prefix)
    for td in data:
        if td.get(key_of_coded_nr) == "1":
            td.append_data({key_of_coded_nc: "1"}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Set messages that weren't relevant as NOT_CODED
    for td in data:
        if td.get(key_of_coded_relevance) == Codes.NO or td.get("noise") is not None:
            td.append_data({key_of_coded_nc: "1"}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Write coded data back out to disk
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output to The Interface
    for td in data:
        td.append_data({
            "district_review_interface": CharacterCleaner.clean_text(td["district_review"]),
            "gender_review_interface": CharacterCleaner.clean_text(td["gender_review"])
        }, Metadata(user, Metadata.get_call_location(), time.time()))

    IOUtils.ensure_dirs_exist(interface_output_dir)
    TracedDataTheInterfaceIO.export_traced_data_iterable_to_the_interface(
        data, interface_output_dir, "avf_phone_id", "S07E01_Humanitarian_Priorities (Text) - esc4jmcna_activation",
        "S07E01_Humanitarian_Priorities (Time EAT) - esc4jmcna_activation",
        county_key="district_review_interface", gender_key="gender_review_interface")
