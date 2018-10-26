from dateutil.parser import isoparse


class MessageFilters(object):
    @staticmethod
    def filter_test_messages(messages, test_run_key="test_run"):
        return [td for td in messages if not td.get(test_run_key, False)]

    @staticmethod
    def filter_time_range(messages, time_key, start_time, end_time):
        return [td for td in messages if start_time <= isoparse(td[time_key]) <= end_time]

    @staticmethod
    def filter_noise(messages, message_key, noise_fn):
        return [td for td in messages if not noise_fn(td[message_key])]
