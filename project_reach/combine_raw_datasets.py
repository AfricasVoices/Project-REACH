import argparse

from core_data_modules.traced_data import TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO
from core_data_modules.util import IOUtils


class CombineRawDatasets(object):
    @staticmethod
    def combine_raw_datasets(user, messages_dataset, surveys_dataset):
        TracedData.update_iterable(user, "avf_phone_id", messages_dataset, surveys_dataset, "survey_responses")
        return messages_dataset
