#!/usr/bin/python3

#   Author:     Harry O'Malley
#   Date:       22/02/2022
#   File:       autobuilder.py
#
#   Script to monitor a specified filesystem for changes
#   When changes are detected, bash scripts can be executed
#   The user can configure what bash scripts should be executed and when

import handler
import keyboard_input
from helpers import *
import config_manager
import select
import pty
import errno
import watchdog.observers
import time
import os
import sys
import subprocess
import json

BASE_PATH = os.path.dirname(__file__)
CONFIG_PATH = f"{BASE_PATH}"
SCRIPT_PATH = f"{BASE_PATH}/scripts"


class Runner():
    # Main Runner class
    # Instantiates the configuration manager, non blocking input & file monitoring handler
    # Monitors the states of these and executes scripts depending on the configuration
    def __init__(self, watchFolder) -> None:
        self.state = config_manager.ConfigurationManager(CONFIG_PATH)
        # initialise event handler
        self.event_handler = handler.Handler(
            patterns=self.state.patterns)
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(
            self.event_handler, path=watchFolder, recursive=True)
        self.observer.start()
        # start listening for input
        self.input = keyboard_input.NonBlockingInput()
        self.running = True
        self.restarting = False
        pass

    #   Capture the output of cmd with bytes_input to stdin,
    #   with stdin, stdout and stderr as TTYs.
    #   Using simulated terminals to capture colour from the output
    #   Normally, subprocess called scripts will not output ANSI colours
    def tty_capture(self, cmd, output=True):
        mo, so = pty.openpty()  # provide tty to enable line-buffering
        me, se = pty.openpty()
        p = subprocess.Popen(
            cmd,
            bufsize=1, stdout=so, stderr=se,
            close_fds=True)
        for fd in [so, se]:
            os.close(fd)
        timeout = 0.04  # seconds
        readable = [mo, me]
        result = {mo: b'', me: b''}
        try:
            while readable:
                if(self.event_handler.state != 0 and self.state.interrupt == True):
                    print(
                        f"Killing process, handler state: {self.event_handler.state}, {self.state.interrupt}")
                    p.kill()
                    p.wait()
                    self.restarting = True
                    return None
                ready, _, _ = select.select(readable, [], [], timeout)
                for fd in ready:
                    try:
                        data = os.read(fd, 512)
                    except OSError as e:
                        if e.errno != errno.EIO:
                            raise
                        # EIO means EOF on some systems
                        readable.remove(fd)
                    else:
                        if not data:  # EOF
                            readable.remove(fd)

                        result[fd] += data
                        # if not running silently, decode and output the read line
                        if(output):
                            print(data.decode('UTF-8'), end="")
        finally:
            for fd in [mo, me]:
                os.close(fd)
            if p.poll() is None:
                p.kill()
            p.wait()
        return result[mo], result[me]

    # Calls run() to load the tests
    def loadTests(self):
        tests_output = self.run("list-tests", output=False)
        if not tests_output:
            return
        output = json.loads(tests_output)
        for test in output.get("tests"):
            name = test.get("name")
            self.state.addTest(name)

    # Takes the script name to run, find the filename in the config and calls
    # tty_capture with the parameters
    def run(self, op, args=None, output=True):
        filename = self.state.script_paths.get(op)
        if not filename:
            print(c(f"ERROR: Could not find {op} script", "red"))
        path = f"{SCRIPT_PATH}/{filename}"
        if(output):
            print(f"Running script: {filename}")
        command = []
        if(args):
            command = [path, *args]
        else:
            command = path
        try:
            completed = self.tty_capture(command, output=output)
            if not completed:
                return None
            output, err = completed
            if(err):
                print(red(
                    f"\n{op.capitalize()} encountered an error during execution:\n"))
                print(err.decode("UTF-8"))
            return output
        except Exception as e:
            print(red(f"ERROR when running {op}\n{e}"))

    # Creates the test string argument to pass to CTest and calls run()

    def test(self):
        args = []
        testString = ''
        tests = self.state.getTests(onlyActive=True)
        # create the argument string to pass to ctest
        for test in tests:
            if(testString.__len__() > 0):
                testString += "|"
            testString += test
        arg = f"-R ({testString})"
        if(self.state.verbose):
            arg = arg + " -V"
        self.run("test", [arg])

    # Is called when the state has changed, check the configuration to see what stages should be executed
    # Calls run() to invoke the specified script
    def execute(self, clean=False):
        if(self.state.periodic_clean and self.state.num_builds >= self.state.num_builds_clean):
            clean = True
        if(clean or self.state.always_clean):
            self.run("clean")
        if(self.state.stages.get("build")):
            if(self.state.stages.get("clang-tidy")):
                self.run("clang-tidy")
            else:
                self.run("build")

        if(self.state.stages.get("test")):
            self.test()
            if(self.state.stages.get("coverage")):
                self.run("coverage")
        if(self.state.stages.get("clang-format")):
            self.run("clang-format")
        # # State hasnt changed yet, meaning we can reset modifications
        # if(self.event_handler.state == 0):
        #     self.event_handler.resetMods()
        self.loadTests()

    # Check if non blocking input class has a keypress queued
    # If it does, the corresponding action is executed
    def checkInput(self):
        if(self.input.input_queued()):
            self.input.stop()
            new_input = self.input.input_get()

            # check input here and configure the watcher
            if(new_input == "q"):
                self.stop()
            elif(new_input == "e"):
                self.state.editConfig()
            elif(new_input == "t"):
                self.state.editTests()
            elif(new_input == "c"):
                self.execute(clean=True)
            elif(new_input == "ca"):
                clearTerminal()
                self.state.setOptions(
                    always_clean=(not self.state.always_clean))
            elif(new_input == "cf"):
                response = input(
                    "Please input the number of builds required to trigger a clean: ")
                clearTerminal()
                self.state.setOptions(num_builds_clean=int(response))
            elif(new_input == "ct"):
                clearTerminal()
                self.state.setOptions(
                    periodic_clean=(not self.state.periodic_clean))
            elif(new_input == "n"):
                response = input(
                    "Please input the number of saves required to trigger a build: ")
                clearTerminal()
                self.state.setOptions(
                    build_interval=int(response))
            elif(new_input == "s"):
                clearTerminal()
                self.state.setOptions(
                    show_options=(not self.state.show_options))
            elif(new_input == "h"):
                clearTerminal()
                self.state.setOptions(
                    show_tests=(not self.state.show_tests))
            elif(new_input == "v"):
                clearTerminal()
                self.state.setOptions(
                    verbose=(not self.state.verbose))
            elif(new_input == "i"):
                clearTerminal()
                self.state.setOptions(
                    interrupt=(not self.state.interrupt))
            elif(new_input == "p"):
                newPattern = input(
                    "Please input the matching pattern you would like to add: ")
                clearTerminal()
                self.state.setOptions(
                    patterns=[*self.state.patterns, newPattern])
            elif(new_input == ""):
                self.execute()
            self.state.printInfo(clear=False)
            self.input.start()
        else:
            return None

    def mainLoop(self):
        # build before doing anything
        # self.run("build")
        self.loadTests()
        self.state.printInfo()
        try:
            while self.running:
                state = self.event_handler.state
                if(state == 0):
                    self.checkInput()
                    time.sleep(0.1)
                else:
                    if(state == 1):
                        if(self.restarting):
                            self.event_handler.resetState()
                            self.restarting = False
                            self.execute()
                        if(self.event_handler.modifications >= self.state.build_interval):
                            self.event_handler.resetState()
                            self.event_handler.resetMods()
                            self.execute()
                        else:
                            time.sleep(0.1)
                            continue
                    elif(state == 2):
                        self.event_handler.resetState()
                        self.event_handler.resetMods()
                        self.execute(clean=True)
                    else:
                        self.event_handler.resetState()
                    self.state.printInfo(clear=False)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("Stopping...")
        self.observer.stop()
        self.observer.join()
        sys.exit(0)


if __name__ == "__main__":
    try:
        watchFolder = sys.argv[1]
    except:
        print(f'''{red("Please pass the folder to be monitored as an argument")}
        i.e.  autobuilder.py {blue("./src/", True)}<-
        ''')
        sys.exit(1)

    runner = Runner(watchFolder)
    runner.mainLoop()
