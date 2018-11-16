import os
import time
from os import path

from core_data_modules.cleaners import somali, Codes, PhoneCleaner
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCodaIO
from core_data_modules.util import IOUtils

from project_reach.lib import Channels


class AutoCodeSurveys(object):
    @staticmethod
    def auto_code_surveys(user, data, phone_uuid_table, coded_output_path, prev_coded_path):
        class CleaningPlan:
            def __init__(self, raw_field, clean_field, coda_name, cleaner):
                self.raw_field = raw_field
                self.clean_field = clean_field
                self.coda_name = coda_name
                self.cleaner = cleaner

        cleaning_plan = [
            CleaningPlan("gender_review", "gender_clean", "Gender",
                         somali.DemographicCleaner.clean_gender),
            CleaningPlan("district_review", "district_clean", "District",
                         somali.DemographicCleaner.clean_somalia_district),
            CleaningPlan("urban_rural_review", "urban_rural_clean", "Urban_Rural",
                         somali.DemographicCleaner.clean_urban_rural),
            CleaningPlan("age_review", "age_clean", "Age",
                         somali.DemographicCleaner.clean_age),
            CleaningPlan("assessment_review", "assessment_clean", "Assessment",
                         somali.DemographicCleaner.clean_yes_no),
            CleaningPlan("idp_review", "idp_clean", "IDP",
                         somali.DemographicCleaner.clean_yes_no),

            CleaningPlan("involved_esc4jmcna", "involved_esc4jmcna_clean", "Involved",
                         somali.DemographicCleaner.clean_yes_no),
            CleaningPlan("repeated_esc4jmcna", "repeated_esc4jmcna_clean", "Repeated",
                         somali.DemographicCleaner.clean_yes_no)
        ]

        # Mark missing entries in the raw data as true missing
        for td in data:
            missing = dict()
            for plan in cleaning_plan:
                if plan.raw_field not in td:
                    missing[plan.raw_field] = Codes.TRUE_MISSING
            td.append_data(missing, Metadata(user, Metadata.get_call_location(), time.time()))

        # Clean all responses
        for td in data:
            cleaned = dict()
            for plan in cleaning_plan:
                if plan.cleaner is not None:
                    cleaned[plan.clean_field] = plan.cleaner(td[plan.raw_field])
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
        for plan in cleaning_plan:
            coded_output_file_path = path.join(coded_output_path, "{}.csv".format(plan.coda_name))
            prev_coded_output_file_path = path.join(prev_coded_path, "{}_coded.csv".format(plan.coda_name))

            if os.path.exists(prev_coded_output_file_path):
                with open(coded_output_file_path, "w") as f, open(prev_coded_output_file_path, "r") as prev_f:
                    TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                        data, plan.raw_field, {plan.coda_name: plan.clean_field}, f, prev_f)
            else:
                with open(coded_output_file_path, "w") as f:
                    TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                        data, plan.raw_field, {plan.coda_name: plan.clean_field}, f)

        return data
