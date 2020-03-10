#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Do-nothing script for making a release

This idea comes from here: 
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

Author: Gertjan van den Burg
Date: 2019-07-23

"""

import colorama
import os


def colored(msg, color=None, style=None):
    colors = {
        "red": colorama.Fore.RED,
        "green": colorama.Fore.GREEN,
        "cyan": colorama.Fore.CYAN,
        "yellow": colorama.Fore.YELLOW,
        "magenta": colorama.Fore.MAGENTA,
        None: "",
    }
    styles = {
        "bright": colorama.Style.BRIGHT,
        "dim": colorama.Style.DIM,
        None: "",
    }
    pre = colors[color] + styles[style]
    post = colorama.Style.RESET_ALL
    return f"{pre}{msg}{post}"


def cprint(msg, color=None, style=None):
    print(colored(msg, color=color, style=style))


def wait_for_enter():
    input(colored("\nPress Enter to continue", style="dim"))
    print()


def get_package_name():
    with open("./setup.py", "r") as fp:
        nameline = next(
            (l.strip() for l in fp if l.startswith("NAME = ")), None
        )
        return nameline.split("=")[-1].strip().strip('"')


class Step:
    def pre(self, context):
        pass

    def post(self, context):
        wait_for_enter()

    def run(self, context):
        try:
            self.pre(context)
            self.action(context)
            self.post(context)
        except KeyboardInterrupt:
            cprint("\nInterrupted.", color="red")
            raise SystemExit(1)

    def instruct(self, msg):
        cprint(msg, color="green")

    def print_run(self, msg):
        cprint("Run:", color="cyan", style="bright")
        self.print_cmd(msg)

    def print_cmd(self, msg):
        cprint("\t" + msg, color="cyan", style="bright")

    def do_cmd(self, cmd):
        cprint(f"Going to run: {cmd}", color="magenta", style="bright")
        wait_for_enter()
        os.system(cmd)


class GitToMaster(Step):
    def action(self, context):
        self.instruct("Make sure you're on master and changes are merged in")
        self.print_run("git checkout master")


class UpdateChangelog(Step):
    def action(self, context):
        self.instruct(f"Update change log for version {context['version']}")
        self.print_run("vi CHANGELOG.md")


class RunTests(Step):
    def action(self, context):
        self.instruct("Run the unit tests")
        self.print_run("make test")


class BumpVersionPackage(Step):
    def action(self, context):
        self.instruct(f"Update __version__.py with new version")
        self.print_run(f"vi {context['pkgname']}/__version__.py")

    def post(self, context):
        wait_for_enter()
        context["version"] = self._get_version(context)

    def _get_version(self, context):
        # Get the version from the version file
        about = {}
        with open(f"{context['pkgname'].lower()}/__version__.py", "r") as fp:
            exec(fp.read(), about)
        return about["__version__"]


class MakeClean(Step):
    def action(self, context):
        self.do_cmd("make clean")


class MakeDocs(Step):
    def action(self, context):
        self.do_cmd("make docs")


class MakeDist(Step):
    def action(self, context):
        self.do_cmd("make dist")


class PushToTestPyPI(Step):
    def action(self, context):
        self.do_cmd(
            "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
        )


class InstallFromTestPyPI(Step):
    def action(self, context):
        self.print_run("cd /tmp/")
        self.print_cmd("rm -rf ./venv")
        self.print_cmd("virtualenv ./venv")
        self.print_cmd("cd ./venv")
        self.print_cmd("source bin/activate")
        self.print_cmd(
            "pip install --index-url https://test.pypi.org/simple/ "
            + f"--extra-index-url https://pypi.org/simple {context['pkgname']}=={context['version']}"
        )


class TestPackage(Step):
    def action(self, context):
        self.instruct(
            f"Ensure that the following command gives version {context['version']}"
        )
        self.print_run(f"p2r -h")


class DeactivateVenv(Step):
    def action(self, context):
        self.print_run("deactivate")
        self.instruct("Go back to the project directory")


class GitTagVersion(Step):
    def action(self, context):
        self.do_cmd(f"git tag v{context['version']}")


class GitAdd(Step):
    def action(self, context):
        self.instruct("Add everything to git and commit")
        self.print_run("git gui")


class PushToPyPI(Step):
    def action(self, context):
        self.do_cmd("twine upload dist/*")


class PushToGitHub(Step):
    def action(self, context):
        self.do_cmd("git push -u --tags origin master")


class WaitForTravis(Step):
    def action(self, context):
        self.instruct(
            "Wait for Travis to complete and verify that its successful"
        )


class WaitForAppVeyor(Step):
    def action(self, context):
        self.instruct(
            "Wait for AppVeyor to complete and verify that its successful"
        )


class WaitForRTD(Step):
    def action(self, context):
        self.instruct(
            "Wait for ReadTheDocs to complete and verify that its successful"
        )


def main():
    colorama.init()
    procedure = [
        GitToMaster(),
        GitAdd(),
        PushToGitHub(),
        BumpVersionPackage(),
        UpdateChangelog(),
        MakeClean(),
        RunTests(),
        MakeDist(),
        PushToTestPyPI(),
        InstallFromTestPyPI(),
        TestPackage(),
        DeactivateVenv(),
        GitAdd(),
        PushToPyPI(),
        GitTagVersion(),
        PushToGitHub(),
    ]
    context = {}
    context["pkgname"] = get_package_name()
    for step in procedure:
        step.run(context)
    cprint("\nDone!", color="yellow", style="bright")


if __name__ == "__main__":
    main()
