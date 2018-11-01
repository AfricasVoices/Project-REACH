from dateutil.parser import isoparse


# TODO: Move to Core once adapted for and tested on a pipeline supports multiple radio shows
class MessageFilters(object):
    # TODO: Log which data is being dropped?
    @staticmethod
    def filter_test_messages(messages, test_run_key="test_run"):
        return [td for td in messages if not td.get(test_run_key, False)]

    @staticmethod
    def filter_time_range(messages, time_key, start_time, end_time):
        return [td for td in messages if start_time <= isoparse(td.get(time_key)) <= end_time]

    @staticmethod
    def filter_noise(messages, message_key, noise_fn):
        return [td for td in messages if not noise_fn(td.get(message_key))]
