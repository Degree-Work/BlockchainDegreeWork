import os
import warnings
from datetime import datetime
from multiprocessing import Process, Queue

import matplotlib.pyplot as plt
import numpy as np

from block import genesis_block, adjust_difficulty, Block
from config.config import *
from utils.crypto_hash import crypto_hash, binary_representation
from utils.date_utils import now_timestamp

# для того, чтобы не засорять вывод предупреждениями
warnings.filterwarnings('ignore')

plt.rcParams["figure.figsize"] = (10, 10)


class BlockchainProcess():
    def __init__(self, name, queue, channels):
        self.name = name
        self.chain = [genesis_block()]
        self.size = 1
        self.queue = queue
        self.channels = channels
        self.run()

    def run(self):
        print('Starting blockchain {} => {}'.format(self.name, os.getpid()))
        while self.size < MAX_COUNT_BLOCKS:
            self.check_channels()
            self.mining(datetime.now())
        print('Finished blockchain %s.' % self.name)

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
            # print('Неудачная попыка замены на: {} | Входящая цепочка должна быть длиннее {} <> {}'
            #      .format(self.name, len(chain), len(self.chain)))
            return

        if not self.is_valid_chain(chain):
            # print("Входящая цепочка должна быть valid")
            return

        #print('Произошла замена на {} => {}'.format(self.name, len(chain)))
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
        """
        Проверка на то есть ли новости от других майнеров/блокчейнов.
        :return: true - что-то есть новое, false - новостей нет
        """
        if not self.queue.empty():
            chain = self.queue.get()
            # print('Channel NOT EMPTY {} => {}'.format(self.name, os.getpid()))
            self.replace_chain(chain)
            return True
        else:
            return False

    def print(self):
        print("Blockchain: " + str(self.name) + " " + str(len(self.chain)))


def initial_blockchain(name, queue, channels):
    blockchain = BlockchainProcess(name, queue, channels)
    arr = [0]
    chain = blockchain.chain
    for i in range(1, len(chain)):
        arr.append(chain[i].timestamp - chain[i - 1].timestamp)
        #chain[i].print()
    iter = np.arange(1, MAX_COUNT_BLOCKS + 1)
    times = [0]
    difficulties = [INITIAL_DIFFICULTY]
    for i in range(1, len(chain)):
        prev_timestamp = chain[i - 1].timestamp
        current_timestamp = chain[i].timestamp
        time_diff = current_timestamp - prev_timestamp
        times.append(time_diff)
        difficulties.append(chain[i].difficulty)
    all_time = chain[-1].timestamp - chain[0].timestamp
    legends = []
    legends.append("Mine rate = " + str(MINE_RATE) + "ms")
    legends.append("Count blocks = " + str(MAX_COUNT_BLOCKS))
    legends.append("Average rate = " + str(all_time / MAX_COUNT_BLOCKS) + "ms")
    legends.append("Full time = " + str(all_time) + "ms")
    # Prepare Data
    # Create as many colors as there are unique midwest['category']
    scatter = plt.scatter(iter, times, c=difficulties, cmap='brg_r')
    plt.title('Time mining blocks where {} participants'.format(THREADS_COUNT))
    plt.ylabel('Mining Time')
    plt.xlabel('Blocks')

    plt.legend(handles=scatter.legend_elements()[0], loc='upper left', labels=legends)
    plt.colorbar()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    n = THREADS_COUNT

    queues = []
    for i in range(n):
        queues.append(Queue())

    producers = []
    for i in range(n):
        number = "#" + str(i)
        producers.append(Process(target=initial_blockchain, args=(number, queues[i], queues[:i] + queues[i + 1:])))

    # Запуск производителей и потребителей.
    # Виртуальная машина Python запускает новые независимые процессы для каждого объекта Process.
    for p in producers:
        p.start()

    # Как и в случае с потоками, у нас есть метод join (), который синхронизирует нашу программу.
    for p in producers:
        p.join()

    print('Parent process exiting...')
