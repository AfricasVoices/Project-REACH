import random


# TODO: Move to Core
class ICRTools(object):
    @staticmethod
    def generate_sample_for_icr(data, sample_size, random_generator=None):
        # FIXME: Should data be de-duplicated before exporting for ICR?

        if random_generator is None:
            random_generator = random

        return random_generator.sample(data, sample_size)
