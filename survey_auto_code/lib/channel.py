import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from dateutil.parser import isoparse


class Channels(object):
    BULK_SMS_KEY = "bulk_sms"
    SMS_AD_KEY = "sms_ad"
    RADIO_PROMO_KEY = "radio_promo"
    RADIO_SHOW_KEY = "radio_show"
    NON_LOGICAL_KEY = "non_logical_time"

    BULK_SMS_RANGES = []  # TODO once the bulk SMS messages have been transmitted
    SMS_AD_RANGES = [
        ("2018-09-09T19:00:00+03:00", "2018-09-10T07:00:00+03:00")
    ]
    RADIO_PROMO_RANGES = [
        ("2018-09-09T00:00:00+03:00", "2018-09-09T19:00:00+03:00"),
        ("2018-09-10T07:00:00+03:00", "2018-09-11T23:59:00+03:00")
    ]
    RADIO_SHOW_RANGES = [
        ("2018-09-14T07:00:00+03:00", "2018-09-15T16:00:00+03:00")
    ]

    RANGES = {
        BULK_SMS_KEY: BULK_SMS_RANGES,
        SMS_AD_KEY: SMS_AD_RANGES,
        RADIO_PROMO_KEY: RADIO_PROMO_RANGES,
        RADIO_SHOW_KEY: RADIO_SHOW_RANGES
    }

    @staticmethod
    def timestamp_is_in_ranges(timestamp, ranges):
        for range in ranges:
            if isoparse(range[0]) <= timestamp < isoparse(range[1]):
                return True
        return False

    @classmethod
    def set_channel_keys(cls, user, td):
        timestamp_key = "S07E01_Humanitarian_Priorities (Time) - esc4jmcna_activation"
        timestamp = isoparse(td[timestamp_key])

        channel_dict = dict()
        time_range_matches = 0
        for key, ranges in cls.RANGES.items():
            if cls.timestamp_is_in_ranges(timestamp, ranges):
                time_range_matches += 1
                channel_dict[key] = Codes.TRUE
            else:
                channel_dict[key] = Codes.FALSE

        if time_range_matches == 0:
            channel_dict[cls.NON_LOGICAL_KEY] = Codes.TRUE
        else:
            channel_dict[cls.NON_LOGICAL_KEY] = Codes.FALSE

        td.append_data(channel_dict, Metadata(user, Metadata.get_call_location(), time.time()))
