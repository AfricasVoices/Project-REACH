import os
import os
import random
import time

import pytz
from core_data_modules.cleaners import somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCodaIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

from project_reach.lib.message_filters import MessageFilters


class AutoCodeShowMessages(object):
    @staticmethod
    def auto_code_show_messages(user, data, icr_output_path, coda_output_path, prev_coda_path):
        variable_name = "S07E01_Humanitarian_Priorities"
        flow_name = "esc4jmcna_activation"
        project_start_date = isoparse("2018-09-09T00+03:00")
        project_end_date = isoparse("2018-09-17T00+03:00")
        show_message_key = "{} (Text) - {}".format(variable_name, flow_name)

        ICR_MESSAGES_COUNT = 200

        # Filter out test messages sent by AVF.
        data = MessageFilters.filter_test_messages(data)

        # Filter for runs which contain a response to this week's question.
        data = [td for td in data if show_message_key in td]

        # Convert date/time of messages to EAT and filter out messages sent outwith the project run period
        utc_key = "{} (Time) - {}".format(variable_name, flow_name)
        eat_key = "{} (Time EAT) - {}".format(variable_name, flow_name)
        for td in data:
            utc_time = isoparse(td[utc_key])
            eat_time = utc_time.astimezone(pytz.timezone("Africa/Nairobi")).isoformat()

            td.append_data(
                {eat_key: eat_time},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

        # Filter out messages sent outwith the project run period
        time_key = "{} (Time) - {}".format(variable_name, flow_name)
        data = MessageFilters.filter_time_range(data, time_key, project_start_date, project_end_date)

        # Identify messages which aren't noise, for export to Coda
        not_noise = MessageFilters.filter_noise(
            data, show_message_key, lambda msg: somali.DemographicCleaner.is_noise(msg, min_length=20))

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

        return data
