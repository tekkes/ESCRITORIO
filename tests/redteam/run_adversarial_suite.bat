@echo off
setlocal
cd /d "%~dp0\..\.."
python "%~dp0run_adversarial_suite.py" %*
exit /b %ERRORLEVEL%
