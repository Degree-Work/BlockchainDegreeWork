import math
from datetime import datetime


def now_timestamp():
    return math.ceil(datetime.now().timestamp() * 1000)
