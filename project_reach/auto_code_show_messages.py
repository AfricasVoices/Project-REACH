import os
import os
import random
import time

from core_data_modules.cleaners import somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCodaIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse


class AutoCodeShowMessages(object):
    @staticmethod
    def auto_code_show_messages(user, show_messages, icr_output_path, coda_output_path, prev_coda_path):
        variable_name = "S07E01_Humanitarian_Priorities"
        flow_name = "esc4jmcna_activation"

        ICR_MESSAGES_COUNT = 200

        # Filter out test messages sent by AVF.
        show_messages = [td for td in show_messages if not td.get("test_run", False)]

        # Filter for runs which contain a response to this week's question.
        show_message_key = "{} (Text) - {}".format(variable_name, flow_name)
        show_messages = [td for td in show_messages if show_message_key in td]

        # Convert date/time of messages to EAT and filter out messages sent outwith the project run period
        utc_key = "{} (Time) - {}".format(variable_name, flow_name)
        inside_time_window = []
        START_TIME = isoparse("2018-09-09T00+03:00")
        END_TIME = isoparse("2018-09-17T00+03:00")
        for td in show_messages:
            utc_time = isoparse(td[utc_key])

            if START_TIME <= utc_time <= END_TIME:
                inside_time_window.append(td)
            else:
                print("Dropping: {}".format(utc_time))

        print("{}:{} Dropped as outside time/Total".format(len(show_messages) - len(inside_time_window),
                                                           len(show_messages)))
        show_messages = inside_time_window

        # Filter out messages containing only noise
        print("Messages classified as noise:")
        not_noise = []
        for td in show_messages:
            if somali.DemographicCleaner.is_noise(td[show_message_key], min_length=20):
                print("Dropping: {}".format(td[show_message_key]))
                td.append_data({"noise": "true"}, Metadata(user, Metadata.get_call_location(), time.time()))
            else:
                not_noise.append(td)

        print("{}:{} Dropped as noise/Total".format(len(show_messages) - len(not_noise), len(show_messages)))

        # Output messages which aren't noise to Coda
        IOUtils.ensure_dirs_exist_for_file(coda_output_path)
        if os.path.exists(prev_coda_path):
            # TODO: Modifying this line once the coding frame has been developed to include lots of Nones feels a bit
            # TODO: cumbersome. We could instead modify export_traced_data_iterable_to_coda to support a prev_f argument
            scheme_keys = {"Relevance": None, "Code 1": None, "Code 2": None, "Code 3": None, "Code 4": None}
            with open(coda_output_path, "w") as f, open(prev_coda_path, "r") as prev_f:
                TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                    not_noise, show_message_key, scheme_keys, f, prev_f=prev_f)
        else:
            with open(coda_output_path, "w") as f:
                TracedDataCodaIO.export_traced_data_iterable_to_coda(not_noise, show_message_key, f)

        # Randomly select some messages to export for ICR
        random.seed(0)
        random.shuffle(not_noise)
        icr_messages = not_noise[:ICR_MESSAGES_COUNT]

        # Output ICR data to a CSV file
        run_id_key = "{} (Run ID) - {}".format(variable_name, flow_name)
        raw_text_key = "{} (Text) - {}".format(variable_name, flow_name)
        IOUtils.ensure_dirs_exist_for_file(icr_output_path)
        with open(icr_output_path, "w") as f:
            TracedDataCSVIO.export_traced_data_iterable_to_csv(icr_messages, f, headers=[run_id_key, raw_text_key])

        return show_messages
