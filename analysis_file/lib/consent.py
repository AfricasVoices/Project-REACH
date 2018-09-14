import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata


class Consent(object):
    @staticmethod
    def td_has_stop_code(td, keys):
        for key in keys:
            if td.get(key) == Codes.STOP:
                return True
        return False

    @classmethod
    def determine_consent(cls, user, data, keys):
        for td in data:
            td.append_data(
                {"withdrawn_consent": Codes.TRUE if cls.td_has_stop_code(td, keys) else Codes.FALSE},
                Metadata(user, Metadata.get_call_location(), time.time()))
            
    @staticmethod
    def set_stopped(user, data, keys):
        for td in data:
            if td["withdrawn_consent"] == Codes.TRUE:
                stop_dict = dict()
                for key in keys:
                    stop_dict[key] = "stop"
                td.append_data(stop_dict, Metadata(user, Metadata.get_call_location(), time.time()))
