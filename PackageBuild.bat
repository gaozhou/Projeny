@echo off

set PYTHONPATH=%~dp0\Source;%PYTHONPATH%
cd %~dp0\Source
python -m upm.main.PackageBuild %*