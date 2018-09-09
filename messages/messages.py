import argparse
import random
import time

import pytz
from core_data_modules.cleaners import somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO, \
    TracedDataTheInterfaceIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans a list of messages, and outputs to formats "
                                                 "suitable for subsequent analysis")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to the input JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("flow_name", metavar="flow-name",
                        help="Name of activation flow from which this data was derived")
    parser.add_argument("variable_name", metavar="variable-name",
                        help="Name of message variable in flow")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed messages to")
    parser.add_argument("interface_output_dir", metavar="interface-output-dir",
                        help="Path to a directory to write The Interface files to")
    parser.add_argument("icr_output_path", metavar="icr-output-path",
                        help="Path to a CSV file to write 200 messages and run ids to, for the purposes of testing"
                             "inter-coder reliability"),
    parser.add_argument("coda_output_path", metavar="coda-output-path",
                        help="Path to a Coda file to write processed messages to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    variable_name = args.variable_name
    flow_name = args.flow_name
    json_output_path = args.json_output_path
    interface_output_dir = args.interface_output_dir
    icr_output_path = args.icr_output_path
    coda_output_path = args.coda_output_path

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        show_messages = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Filter out test messages sent by AVF.
    show_messages = [td for td in show_messages if not td.get("test_run", False)]

    # Filter for runs which contain a response to this week's question.
    show_message_key = "{} (Text) - {}".format(variable_name, flow_name)
    show_messages = [td for td in show_messages if show_message_key in td]

    # Filter out messages containing only noise
    print("Messages classed as noise:")
    not_noise = []
    for td in show_messages:
        if somali.DemographicCleaner.is_noise(td[show_message_key]):
            print(td[show_message_key])
        else:
            not_noise.append(td)
    show_messages = not_noise

    # Convert date/time of messages to EAT
    utc_key = "{} (Time) - {}".format(variable_name, flow_name)
    eat_key = "{} (Time EAT) - {}".format(variable_name, flow_name)
    for td in show_messages:
        utc_time = isoparse(td[utc_key])
        eat_time = utc_time.astimezone(pytz.timezone("Africa/Nairobi")).isoformat()

        td.append_data(
            {eat_key: eat_time},
            Metadata(user, Metadata.get_call_location(), time.time())
        )

    # Take 200 items pseudo-randomly for ICR
    random.seed(0)
    random.shuffle(show_messages)
    icr_messages = show_messages[:200]

    # Output to JSON
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(show_messages, f, pretty_print=True)

    # Output to The Interface
    IOUtils.ensure_dirs_exist(interface_output_dir)
    TracedDataTheInterfaceIO.export_traced_data_iterable_to_the_interface(
        show_messages, interface_output_dir, "avf_phone_id", show_message_key, eat_key)

    # Output messages to Coda
    IOUtils.ensure_dirs_exist_for_file(coda_output_path)
    with open(coda_output_path, "w") as f:
        TracedDataCodaIO.export_traced_data_iterable_to_coda(
            show_messages, "{} (Text) - {}".format(variable_name, flow_name), f)

    # Write ICR data to a file
    run_id_key = "{} (Run ID) - {}".format(variable_name, flow_name)
    raw_text_key = "{} (Text) - {}".format(variable_name, flow_name)
    IOUtils.ensure_dirs_exist_for_file(icr_output_path)
    with open(icr_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(icr_messages, f, headers=[run_id_key, raw_text_key])
