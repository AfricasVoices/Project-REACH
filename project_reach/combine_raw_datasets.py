from core_data_modules.traced_data import TracedData


class CombineRawDatasets(object):
    @staticmethod
    def combine_raw_datasets(user, messages_dataset, surveys_dataset):
        TracedData.update_iterable(user, "avf_phone_id", messages_dataset, surveys_dataset, "survey_responses")
        return messages_dataset
