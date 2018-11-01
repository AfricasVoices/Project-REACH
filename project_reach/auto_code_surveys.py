import os
import time
from os import path

from core_data_modules.cleaners import Codes, PhoneCleaner
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCodaIO
from core_data_modules.util import IOUtils

from project_reach.lib.channel import Channels
from project_reach.lib.dataset_specification import DatasetSpecification


class AutoCodeSurveys(object):
    @staticmethod
    def auto_code_surveys(user, data, phone_uuid_table, coded_output_path, prev_coded_path):
        # Mark missing entries in the raw data as true missing
        for td in data:
            missing = dict()
            for plan in DatasetSpecification.coding_plans:
                if plan.source_field not in td:
                    missing[plan.source_field] = Codes.TRUE_MISSING
            td.append_data(missing, Metadata(user, Metadata.get_call_location(), time.time()))

        # Clean all responses
        for td in data:
            cleaned = dict()
            for plan in DatasetSpecification.coding_plans:
                if plan.cleaner is not None:
                    cleaned[plan.auto_coded_field] = plan.cleaner(td[plan.source_field])
            td.append_data(cleaned, Metadata(user, Metadata.get_call_location(), time.time()))

        # Label each message with the operator of the sender
        for td in data:
            phone_number = phone_uuid_table.get_phone(td["avf_phone_id"])
            operator = PhoneCleaner.clean_operator(phone_number)

            td.append_data(
                {"operator": operator},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

        # Label each message with channel keys
        for td in data:
            Channels.set_channel_keys(user, td)

        # Output for manual verification + coding
        IOUtils.ensure_dirs_exist(coded_output_path)
        for plan in DatasetSpecification.coding_plans:
            coded_output_file_path = path.join(coded_output_path, "{}.csv".format(plan.coda_name))
            prev_coded_output_file_path = path.join(prev_coded_path, "{}_coded.csv".format(plan.coda_name))

            if os.path.exists(prev_coded_output_file_path):
                with open(coded_output_file_path, "w") as f, open(prev_coded_output_file_path, "r") as prev_f:
                    TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                        data, plan.source_field, {plan.coda_name: plan.manually_coded_field}, f, prev_f)
            else:
                with open(coded_output_file_path, "w") as f:
                    TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                        data, plan.source_field, {plan.coda_name: plan.manually_coded_field}, f)

        return data
