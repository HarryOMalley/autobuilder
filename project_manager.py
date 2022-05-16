from time import sleep
from helpers import *
from packaging.version import parse
import questionary
from questionary import Choice
import sys
from logger import logger
VERSION = "1.0"


class ProjectManager():
    # Controls project specific configuration of where the project is, what scripts to run
    # Set the scripts folder to overwrite any/all of the scripts default with autobuilder
    default_config = {
        "version": VERSION,
        "project_path": "",
        "script_folder": None,
        "build_folder": "build",
        "script_paths": {
            "build": "build.sh",
            "test": "test.sh",
            "coverage": "coverage.sh",
            "clang-format": "clang-format.sh",
            "clang-tidy": "clang-tidy.sh",
            "clean": "clean.sh",
            "list-tests": "list-tests.sh"
        },
    }

    def __init__(self, PROJECT_PATH) -> None:
        self.PROJECT_PATH = PROJECT_PATH
        self.config = []
        self.stages = []
        self.script_paths = []
        self.patterns = []
        self.always_clean = False
        self.show_options = False
        self.show_tests = False
        self.periodic_clean = False
        self.num_builds_clean = 0
        self.build_interval = 0
        self.verbose = False
        self.interrupt = False
        self.verifyConfig()
        pass

    def verifyConfig(self):
        # Load config files and verify that they are the right version, load and add tests
        print("Verifying configs")
        config = loadJson(f"{self.PROJECT_PATH}/autobuilder.json")
        if not config:
            self.loadMainConfig(self.default_config)
            self.saveConfig()
            print(f'''\t {green("Created configuration file", True)}
Please review {self.PROJECT_PATH}/autobuilder.json and modify script paths and matching patterns as required
            ''')
            sleep(10)
        else:
            # try to parse the config version, otherwise set as 0
            config_version = parse(config.get("version") or "0.0")
            current_version = parse(VERSION)

            if(config_version == current_version):
                self.loadMainConfig(config)
            else:
                # check if it is a major release discrepancy
                if(current_version.major > config_version.major):
                    renameFile(f"{self.PROJECT_PATH}/autobuilder.json",
                               f"{self.PROJECT_PATH}/autobuilder.old.json")
                    saveJson(self.PROJECT_PATH, "config",
                             self.default_config)
                    clearTerminal()
                    print(f'''\t {red("~~~ ERROR ~~~")}
The autobuilder.json file is from a previous release of autobuilder, a new config has been generated.
The existing autobuilder.json has been renamed to autobuilder.old.json
Please review the new file, modify as required and rerun
                    ''')
                    sleep(5)
                    sys.exit(1)

                # only warn if it is a minor release
                else:
                    saveJson(self.PROJECT_PATH, "config.new",
                             self.default_config)
                    self.loadMainConfig(config)
                    clearTerminal()
                    print(f''' \t{yellow("--- WARNING ---")}
The autobuilder.json file may be out of date
A new file has been generated to config.new.json
Please review and modify your existing configuration if required
(You will need to bump the version number to {VERSION} after reviewing)
Continuing in 30s...
                    ''')
                    sleep(30)

    def saveConfig(self):
        self.config["stages"] = self.stages
        saveJson(self.PROJECT_PATH, "autobuilder", self.config)
        return

    # Takes a config file and loads the properties into the class
    def loadMainConfig(self, config):
        self.stages = config.get("stages")
        self.script_paths = config.get("script_paths")
        self.excluded_tests = config.get("excluded_tests") or []

        options = config.get("options")
        self.patterns = options.get("patterns")
        self.always_clean = options.get("always_clean")
        self.show_options = options.get("show_options")
        self.periodic_clean = options.get("periodic_clean")
        self.num_builds_clean = options.get("num_builds_clean")
        self.build_interval = options.get("build_interval")
        self.show_tests = options.get("show_tests")
        self.verbose = options.get("verbose")
        self.interrupt = options.get("interrupt")
        self.config = config

    def setOptions(self, always_clean=None,
                   show_options=None, periodic_clean=None,
                   num_builds_clean=None, build_interval=None, show_tests=None, patterns=None, verbose=None, interrupt=None):
        if(always_clean is None):
            always_clean = self.always_clean
        if(show_options is None):
            show_options = self.show_options
        if(periodic_clean is None):
            periodic_clean = self.periodic_clean
        if(num_builds_clean is None):
            num_builds_clean = self.num_builds_clean
        if(build_interval is None):
            build_interval = self.build_interval
        if(show_tests is None):
            show_tests = self.show_tests
        if(verbose is None):
            verbose = self.verbose
        if(interrupt is None):
            interrupt = self.interrupt
        if(patterns is None):
            patterns = self.patterns

        self.config["options"] = ({
            "always_clean": always_clean,
            "periodic_clean": periodic_clean,
            "build_interval": build_interval,
            "num_builds_clean": num_builds_clean,
            "patterns": patterns,
            "show_options": show_options,
            "show_tests": show_tests,
            "verbose": verbose,
            "interrupt": interrupt
        })
        self.saveConfig()
        self.loadMainConfig(self.config)

    def listOptions(self, minimal=False):

        if(self.always_clean):
            print(
                purple("\n\t~~~ Always clean build active ~~~"))

        if minimal:
            print(
                f'\n    › Enter {blue("s")} to show options, {blue("h")} to toggle show tests, {red("q")} to exit, or press {green("ENTER")} to run')

        else:
            print(f'''        
    Watch Usage
        › Enter {green("e")} to choose which stages should be ran
                {green("t")} to choose what tests should be ran
                {green("s")} to minimise options
                {green("h")} to hide/show tests
                {green("c")} to trigger a clean build
                {green("cf")} to change how frequently a clean build should run
                {green("ca")} to toggle always clean builds
                {green("ct")} to toggle periodic clean builds
                {green("n")} to change the number of saves to trigger a build
                {green("v")} to toggle verbose testing
                {green("p")} to add a new matching pattern
                {green("i")} to toggle interruptable builds\n
        › Press {blue("ENTER", True)} to trigger a run
        › Enter {red("q", True)} to exit.''')

    def printConfig(self):
        print(f'\n    {bold("Config")}')
        for i in self.stages:
            print(
                f"     › {i.capitalize()} - {bprint(self.stages[i])}")
        print(
            f"\n    Periodic clean builds: \t{bprint(self.periodic_clean)}\tBuild interval: \t{self.build_interval}")
        print(
            f"    Interruptable builds: \t{bprint(self.interrupt)}\tBuilds between clean:\t{self.num_builds_clean}")
        print(f"    Verbose testing: \t{bprint(self.verbose)}")
        print(
            f"    Matching patterns: \t{', '.join(str(x) for x in self.patterns)}\n")

    # go through tests and print them out
    # Optionally filter by what type of test (unit or functional) and whether they are active
    def printTests(self, functional=True, unit=True, filter=False):
        if unit:
            if(self.utests.__len__() > 0):
                tests = []
                for i in self.utests:
                    excluded = True if i in self.excluded_tests else False
                    if(filter):
                        if(excluded):
                            continue
                    tests.append(i)
                if(tests.__len__() > 0):
                    print("    Unit tests")
                    for i in tests:
                        excluded = True if i in self.excluded_tests else False
                        print(f"\t{grey(i) if excluded else blue(i)}")
            else:
                print("No Unit tests detected")
                print(self.utests)
                print(self.tests)
        if functional:
            if(self.ftests.__len__() > 0):
                tests = []
                for i in self.ftests:
                    excluded = True if i in self.excluded_tests else False
                    if(filter):
                        if(excluded):
                            continue
                    tests.append(i)
                if(tests.__len__() > 0):
                    print("    Functional tests")
                    for i in tests:
                        excluded = True if i in self.excluded_tests else False
                        print(f"\t{grey(i) if excluded else blue(i)}")
            else:
                print("No Functional tests detected")
                print(self.ftests)
                print(self.tests)

    # Print the info about the configuration
    def printInfo(self, clear=True):
        if clear:
            clearTerminal()
        if not self.show_options:
            if(self.stages.get("test") and self.show_tests):
                self.printTests(filter=True)
            self.listOptions(minimal=True)
        else:

            self.printConfig()
            if(self.stages.get("test") and self.show_tests):
                self.printTests()
            self.listOptions()

    def updateExcluded(self, new):
        self.excluded_tests = new
        self.config["excluded_tests"] = self.excluded_tests
        self.saveConfig()

    def addTest(self, test):
        # check if test is already in config
        if(test not in self.tests):
            self.tests.append(test)
            if("unit" in test):
                self.utests.append(test)
            elif("ftest" in test):
                self.ftests.append(test)
        return

    # get tests, optionally request only active (non excluded) tests
    def getTests(self, onlyActive=None):
        if(onlyActive):
            activeTests = []
            for test in self.tests:
                if(test in self.excluded_tests):
                    continue
                else:
                    activeTests.append(test)
            return activeTests
        else:
            return self.tests

    def editConfig(self):
        choices = []
        for i in self.stages:
            choices.append(Choice(i, checked=self.stages[i]))
        newChoices = questionary.checkbox(
            "Enable/Disable build options",
            choices=choices
        ).ask()
        for i in self.stages:
            if(i in newChoices):
                self.stages[i] = True
            else:
                self.stages[i] = False
        clearTerminal()
        self.saveConfig()

    def editTests(self):
        choices = []
        for i in self.tests:
            checked = False if i in self.excluded_tests else True
            choices.append(
                Choice(i, checked=checked))
        newChoices = questionary.checkbox(
            "Enable/Disable tests",
            choices=choices
        ).ask()
        newExcluded = []
        for i in self.tests:
            if i not in newChoices:
                newExcluded.append(i)
        self.updateExcluded(newExcluded)
        clearTerminal()
