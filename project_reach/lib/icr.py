import random


# TODO: Move to Core
class ICRTools(object):
    @staticmethod
    def generate_sample_for_icr(data, sample_size, random_seed=0):
        random.seed(random_seed)
        return random.sample(data, sample_size)
