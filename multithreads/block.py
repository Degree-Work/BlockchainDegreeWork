from config.config import INITIAL_DIFFICULTY, MINE_RATE
from utils.date_utils import now_timestamp


class Block:
    def __init__(self, timestamp, last_hash, hash, data, nonce, difficulty):
        self.timestamp = timestamp
        self.last_hash = last_hash
        self.hash = hash
        self.data = data
        self.nonce = nonce
        self.difficulty = difficulty

    def print(self):
        print("Block(timestamp=" + str(self.timestamp) +
              ", last_hash=" + str(self.last_hash) +
              ", hash=" + str(self.hash) +
              ", data=" + str(self.data) +
              ", nonce=" + str(self.nonce) +
              ", difficulty=" + str(self.difficulty))


def genesis_block():
    return Block(now_timestamp(), "---", "hash-one", "data", 0, INITIAL_DIFFICULTY)


def adjust_difficulty(last_block, timestamp):
    difficulty = last_block.difficulty
    if timestamp - last_block.timestamp > MINE_RATE:
        difficulty -= 1
    else:
        difficulty += 1
    if difficulty < 1:
        return 1
    else:
        return difficulty
