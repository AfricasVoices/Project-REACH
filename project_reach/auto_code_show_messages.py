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
    VARIABLE_NAME = "S07E01_Humanitarian_Priorities"
    FLOW_NAME = "esc4jmcna_activation"
    PROJECT_START_DATE = isoparse("2018-09-09T00+03:00")
    PROJECT_END_DATE = isoparse("2018-09-17T00+03:00")
    SHOW_MESSAGE_KEY = "{} (Text) - {}".format(VARIABLE_NAME, FLOW_NAME)
    ICR_MESSAGES_COUNT = 200

    @classmethod
    def auto_code_show_messages(cls, user, data, icr_output_path, coda_output_path, prev_coda_path):
        # Filter out test messages sent by AVF.
        data = MessageFilters.filter_test_messages(data)

        # Filter for runs which contain a response to this week's question.
        data = MessageFilters.filter_empty_messages(data, cls.SHOW_MESSAGE_KEY)

        time_key = "{} (Time) - {}".format(cls.VARIABLE_NAME, cls.FLOW_NAME)
        data = MessageFilters.filter_time_range(data, time_key, cls.PROJECT_START_DATE, cls.PROJECT_END_DATE)

        # Tag messages which are noise as being noise
        for td in data:
            if somali.DemographicCleaner.is_noise(td[cls.SHOW_MESSAGE_KEY], min_length=20):
                td.append_data({"noise": "true"}, Metadata(user, Metadata.get_call_location(), time.time()))

        # Filter for messages which aren't noise (in order to export to Coda and export for ICR)
        not_noise = MessageFilters.filter_noise(data, "noise", lambda x: x)

        # Output messages which aren't noise to Coda
        IOUtils.ensure_dirs_exist_for_file(coda_output_path)
        if os.path.exists(prev_coda_path):
            # TODO: Modifying this line once the coding frame has been developed to include lots of Nones feels a bit
            # TODO: cumbersome. We could instead modify export_traced_data_iterable_to_coda to support a prev_f argument
            scheme_keys = {"Relevance": None, "Code 1": None, "Code 2": None, "Code 3": None, "Code 4": None}
            with open(coda_output_path, "w") as f, open(prev_coda_path, "r") as prev_f:
                TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                    not_noise, cls.SHOW_MESSAGE_KEY, scheme_keys, f, prev_f=prev_f)
        else:
            with open(coda_output_path, "w") as f:
                TracedDataCodaIO.export_traced_data_iterable_to_coda(not_noise, cls.SHOW_MESSAGE_KEY, f)

        # Randomly select some messages to export for ICR
        icr_messages = ICRTools.generate_sample_for_icr(not_noise, cls.ICR_MESSAGES_COUNT, random.Random(0))

        # Output ICR data to a CSV file
        run_id_key = "{} (Run ID) - {}".format(cls.VARIABLE_NAME, cls.FLOW_NAME)
        raw_text_key = "{} (Text) - {}".format(cls.VARIABLE_NAME, cls.FLOW_NAME)
        IOUtils.ensure_dirs_exist_for_file(icr_output_path)
        with open(icr_output_path, "w") as f:
            TracedDataCSVIO.export_traced_data_iterable_to_csv(icr_messages, f, headers=[run_id_key, raw_text_key])

        return data
