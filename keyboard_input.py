
#   Author:     Harry O'Malley
#   Date:       22/02/2022
#   File:       input.py
#
#   Library to allow non-blocking input from the user
#   Used in the autobuilder script to receive keyboard choices from the user
#     without blocking the main monitoring thread


import queue
import threading
from logger import logger


class NonBlockingInput:

    def __init__(self, ):
        # create input queue
        self.input_queue = queue.Queue()
        # instantiate thread to run the read_kbd_input function
        self.input_thread = threading.Thread(
            target=self.read_kbd_input, args=(), daemon=True)
        self.input_thread.start()

    # read_kbd_input is the main loop to be instantiated as a thread
    # Reads one input from the user at a time to prevent blocking
    def read_kbd_input(self):
        self.running = True
        while True:
            while self.running:
                try:
                    console_input = input()
                    self.input_queue.put(console_input)
                    # if input has been read, stop running the monitoring
                    # monitoring can be renabled by the main thread if required
                    self.running = False
                except:
                    logger.error("Exception when reading user input")

    def input_queued(self):
        return_value = False
        if self.input_queue.qsize() > 0:
            return_value = True
        return return_value

    def input_get(self):
        return_value = ""
        if self.input_queue.qsize() > 0:
            return_value = self.input_queue.get()
        return return_value

    def stop(self):
        self.running = False
        return

    def start(self):
        self.running = True
        return
