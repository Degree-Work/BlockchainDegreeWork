import warnings
from datetime import datetime
from multiprocessing import Process, Queue

import matplotlib.pyplot as plt
import numpy as np

from block import genesis_block, adjust_difficulty, Block
from config.config import *
from utils.crypto_hash import crypto_hash, binary_representation
from utils.date_utils import now_timestamp

warnings.filterwarnings('ignore')
plt.rcParams["figure.figsize"] = (12, 12)

class BlockchainProcess():
    def __init__(self, name, queue, channels):
        self.name = name
        self.chain = [genesis_block()]
        self.size = len(self.chain)
        self.queue = queue
        self.channels = channels
        self.run()

    def run(self):
        while self.size < MAX_COUNT_BLOCKS:
            self.check_channels()
            self.mining(datetime.now())

    def mining(self, data):
        last_block = self.chain[-1]
        nonce = 0
        difficulty = last_block.difficulty
        last_hash = last_block.hash
        hash = "F"
        timestamp = now_timestamp()
        check_channels = False
        while binary_representation(hash)[:difficulty] != '0' * difficulty:
            check_channels = self.check_channels()
            if check_channels:
                break
            else:
                nonce += 1
                timestamp = now_timestamp()
                difficulty = adjust_difficulty(last_block, timestamp)
                hash = crypto_hash(timestamp, last_hash, data, nonce, difficulty)
        if not check_channels:
            self.add_block(timestamp, last_hash, hash, data, nonce, difficulty)
            self.notification()

    def add_block(self, timestamp, last_hash, hash, data, nonce, difficulty):
        block = Block(timestamp, last_hash, hash, data, nonce, difficulty)
        self.chain.append(block)
        self.size = len(self.chain)

    def replace_chain(self, chain):
        if len(chain) <= len(self.chain):
            return
        if not self.is_valid_chain(chain):
            return
        self.update(chain)

    @staticmethod
    def is_valid_chain(chain):
        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i - 1]

            if (abs(block.difficulty - last_block.difficulty)) > 1:
                return False

            if last_block.hash != block.last_hash:
                return False
        return True

    def update(self, chain):
        self.chain = chain
        self.size = len(self.chain)

    def notification(self):
        for channel in self.channels:
            channel.put(self.chain)

    def check_channels(self):
        if not self.queue.empty():
            chain = self.queue.get()
            self.replace_chain(chain)
            return True
        else:
            return False


def initial_blockchain(name, queue, channels):
    blockchain = BlockchainProcess(name, queue, channels)

    chain = blockchain.chain
    iter = np.arange(1, MAX_COUNT_BLOCKS + 1)
    times = [0]
    difficulties = [INITIAL_DIFFICULTY]
    deviation_count = 0
    deviation_time_max = 0
    for i in range(1, len(chain)):
        prev_timestamp = chain[i - 1].timestamp
        current_timestamp = chain[i].timestamp
        time_diff = current_timestamp - prev_timestamp
        times.append(time_diff)
        difficulties.append(chain[i].difficulty)
        deviation_time_max = max(deviation_time_max, time_diff)
        if time_diff > MINE_RATE:
            deviation_count += 1

    all_time = chain[-1].timestamp - chain[0].timestamp

    legends = []
    legends.append("Mine rate = " + str(MINE_RATE) + "ms")
    legends.append("Count blocks = " + str(MAX_COUNT_BLOCKS))
    average_time = all_time / MAX_COUNT_BLOCKS
    average_time_percent = round((average_time / MINE_RATE) * 100, 2)
    legends.append("Average rate = " + str(average_time) + "ms = " + str(average_time_percent) + "%")
    legends.append("Full time = " + str(all_time) + "ms")
    legends.append("Deviation Count = " + str(deviation_count))
    deviation_time_max_percent = round((deviation_time_max / MINE_RATE) * 100, 2)
    legends.append("Deviation Time Max = " + str(deviation_time_max) + "ms = " + str(deviation_time_max_percent) + "%")

    scatter = plt.scatter(iter, times, c=difficulties, cmap='brg_r')
    plt.title('Time mining blocks where {} participants'.format(PROCESS_COUNT))
    plt.ylabel('Mining Time')
    plt.xlabel('Blocks')

    plt.legend(handles=scatter.legend_elements()[0], loc='upper left', labels=legends)
    plt.colorbar()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    queues = []
    for i in range(PROCESS_COUNT):
        queues.append(Queue())

    producers = []
    for i in range(PROCESS_COUNT):
        process_name = "#" + str(i)
        producers.append(
            Process(target=initial_blockchain, args=(process_name, queues[i], queues[:i] + queues[i + 1:])))

    for p in producers:
        p.start()

    for p in producers:
        p.join()

    print('Parent process exiting...')
