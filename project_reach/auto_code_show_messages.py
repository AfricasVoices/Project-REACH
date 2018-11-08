import os
import random
import time

from core_data_modules.cleaners import somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCodaIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

from project_reach.lib import ICRTools
from project_reach.lib import MessageFilters


class AutoCodeShowMessages(object):
    @staticmethod
    def auto_code_show_messages(user, data, icr_output_path, coda_output_path, prev_coda_path):
        variable_name = "S07E01_Humanitarian_Priorities"
        flow_name = "esc4jmcna_activation"
        project_start_date = isoparse("2018-09-09T00+03:00")
        project_end_date = isoparse("2018-09-17T00+03:00")
        show_message_key = "{} (Text) - {}".format(variable_name, flow_name)
        icr_messages_count = 200

        # Filter out test messages sent by AVF.
        data = MessageFilters.filter_test_messages(data)

        # Filter for runs which contain a response to this week's question.
        data = [td for td in data if show_message_key in td]

        time_key = "{} (Time) - {}".format(variable_name, flow_name)
        data = MessageFilters.filter_time_range(data, time_key, project_start_date, project_end_date)

        # Identify messages which aren't noise, for export to Coda
        print("Messages classified as noise:")
        not_noise = []
        for td in data:
            if somali.DemographicCleaner.is_noise(td[show_message_key], min_length=20):
                print("Dropping: {}".format(td[show_message_key]))
                td.append_data({"noise": "true"}, Metadata(user, Metadata.get_call_location(), time.time()))
            else:
                not_noise.append(td)

        print("{}:{} Dropped as noise/Total".format(len(data) - len(not_noise), len(data)))

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
        icr_messages = ICRTools.generate_sample_for_icr(not_noise, icr_messages_count, random.Random(0))

        # Output ICR data to a CSV file
        run_id_key = "{} (Run ID) - {}".format(variable_name, flow_name)
        raw_text_key = "{} (Text) - {}".format(variable_name, flow_name)
        IOUtils.ensure_dirs_exist_for_file(icr_output_path)
        with open(icr_output_path, "w") as f:
            TracedDataCSVIO.export_traced_data_iterable_to_csv(icr_messages, f, headers=[run_id_key, raw_text_key])

        return data
