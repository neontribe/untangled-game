@echo off

py -m pip install --user -r requirements.txt

echo What would you like the hostname to be?
set /p HOSTNAME=
@echo %HOSTNAME%

@echo HOSTNAME="%HOSTNAME%"> ecs/config.py