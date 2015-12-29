
import upm.main.Upm as Upm

import os
import upm.ioc.Container as Container
from upm.ioc.Inject import Inject
import upm.ioc.IocAssertions as Assertions
import sys
import argparse

from upm.util.PlatformUtil import Platforms
import upm.util.PlatformUtil as PlatformUtil
from upm.util.Assert import *

class Runner:
    _scriptRunner = Inject('ScriptRunner')
    _log = Inject('Logger')
    _sys = Inject('SystemHelper')
    _varMgr = Inject('VarManager')
    _vsSolutionHelper = Inject('VisualStudioHelper')

    def run(self, args):
        self._args = args
        success = self._scriptRunner.runWrapper(self._runInternal)

        if not success:
            sys.exit(1)

    def _runInternal(self):
        self._log.debug("Started OpenInVisualStudio with arguments: {0}".format(" ".join(sys.argv[1:])))

        project, platform = self._getProjectAndPlatformFromFilePath(self._args.filePath)

        self._log.debug("Determined Project = {0}, Platform = {1}", project, platform)

        lineNo = 1
        if self._args.lineNo:
            lineNo = int(self._args.lineNo)

        self._vsSolutionHelper.openFile(
            self._args.filePath, lineNo, project, platform)

    def _getProjectAndPlatformFromFilePath(self, filePath):
        unityProjectsDir = self._sys.canonicalizePath(self._varMgr.expand('[UnityProjectsDir]'))
        filePath = self._sys.canonicalizePath(filePath)

        if not filePath.startswith(unityProjectsDir):
            raise Exception("The given file path is not within the UnityProjects directory")

        relativePath = filePath[len(unityProjectsDir)+1:]
        dirs = relativePath.split(os.path.sep)

        projectName = dirs[0]

        platformProjectDirName = dirs[1]
        platformDirName = platformProjectDirName[platformProjectDirName.rfind('-')+1:]

        platform = PlatformUtil.fromPlatformFolderName(platformDirName)

        return projectName, platform

def addArguments(parser):
    parser.add_argument("filePath", help="")
    parser.add_argument("lineNo", nargs='?', help="")

def findConfigPath(filePath):
    lastParentDir = None
    parentDir = os.path.dirname(filePath)

    while parentDir and parentDir != lastParentDir:
        configPath = os.path.join(parentDir, Upm.ConfigFileName)

        if os.path.isfile(configPath):
            return configPath

        lastParentDir = parentDir
        parentDir = os.path.dirname(parentDir)

    assertThat(False, "Could not find UPM config path starting at path {0}", filePath)

def installBindings(args):

    Container.bind('LogStream').toSingle(LogStreamConsole, True, False)

    Upm.installBindings([findConfigPath(args.filePath)])

if __name__ == '__main__':
    if (sys.version_info < (3, 0)):
        print('Wrong version of python!  Install python 3 and try again')
        sys.exit(2)

    parser = argparse.ArgumentParser(description='Projeny Visual Studio Opener')
    addArguments(parser)

    argv = sys.argv[1:]

    # If it's 2 then it only has the -cfg param
    if len(argv) == 0:
        parser.print_help()
        sys.exit(2)

    args = parser.parse_args(sys.argv[1:])

    installBindings(args)

    Runner().run(args)

