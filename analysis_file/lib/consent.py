import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata


class Consent(object):
    Codes.STOP = "stop"

    @staticmethod
    def process_stopped(user, data, keys):
        print("Stopped:")
        for td in data:
            stop_dict = dict()
            for key in keys:
                if td.get(key) == "stop":  # TODO: Use Codes.STOP
                    print(td["avf_phone_id"])
                    stop_dict[key] = "stop"
            td.append_data(stop_dict, Metadata(user, Metadata.get_call_location(), time.time()))


