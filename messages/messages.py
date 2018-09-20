import argparse
import os
import time
import random

import pytz
from core_data_modules.cleaners import somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans a list of messages, and outputs to formats "
                                                 "suitable for subsequent analysis")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to the input JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("prev_coda_path", metavar="prev-coda-path",
                        help="Path to a Coda file containing previously coded messages")
    parser.add_argument("flow_name", metavar="flow-name",
                        help="Name of activation flow from which this data was derived")
    parser.add_argument("variable_name", metavar="variable-name",
                        help="Name of message variable in flow")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed messages to")
    parser.add_argument("coda_output_path", metavar="coda-output-path",
                        help="Path to a Coda file to write processed messages to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    prev_coda_path = args.prev_coda_path
    variable_name = args.variable_name
    flow_name = args.flow_name
    json_output_path = args.json_output_path
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
    print("Messages classified as noise:")
    not_noise = []
    for td in show_messages:
        if somali.DemographicCleaner.is_noise(td[show_message_key], min_length=20):
            print("Dropping: {}".format(td[show_message_key]))
        else:
            not_noise.append(td)
    
    print("{}:{} Dropped as noise/Total".format(len(show_messages) - len(not_noise), len(show_messages)))
    show_messages = not_noise

    # Convert date/time of messages to EAT
    utc_key = "{} (Time) - {}".format(variable_name, flow_name)
    eat_key = "{} (Time EAT) - {}".format(variable_name, flow_name)
    inside_time_window = []
    START_TIME = isoparse("2018-09-09T00+03:00")
    END_TIME = isoparse("2018-09-17T00+03:00")

    for td in show_messages:
        utc_time = isoparse(td[utc_key])
        eat_time = utc_time.astimezone(pytz.timezone("Africa/Nairobi")).isoformat()

        td.append_data(
            {eat_key: eat_time},
            Metadata(user, Metadata.get_call_location(), time.time())
        )

        if (utc_time >= START_TIME and utc_time <= END_TIME):
            inside_time_window.append(td)
        else:
            print ("Dropping: {}".format(utc_time))

    print("{}:{} Dropped as outside time/Total".format(len(show_messages) - len(inside_time_window), len(show_messages)))
    show_messages = inside_time_window

    # Output to JSON
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(show_messages, f, pretty_print=True)

    # Output messages to Coda
    IOUtils.ensure_dirs_exist_for_file(coda_output_path)
    if os.path.exists(prev_coda_path):
        # TODO: Modifying this line once the coding frame has been developed to include lots of Nones feels a bit
        # TODO: cumbersome. We could instead modify export_traced_data_iterable_to_coda to support a prev_f argument.
        scheme_keys = {"Relevance": None, "Code 1": None, "Code 2": None, "Code 3": None, "Code 4": None}
        with open(coda_output_path, "w") as f, open(prev_coda_path, "r") as prev_f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                show_messages, show_message_key, scheme_keys, f, prev_f=prev_f)
    else:
        with open(coda_output_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda(show_messages, show_message_key, f)
