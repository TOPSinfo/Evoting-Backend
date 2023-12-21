import random


class Utills(object):
    def get_otp(self, N):
        min = pow(10, N - 1)
        max = pow(10, N) - 1
        return random.randint(min, max)
