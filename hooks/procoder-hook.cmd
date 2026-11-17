@echo off
rem Freebuff procoder hook. %1 is the event (pre|post|stop); the rest are the
rem tool's values, passed straight to the bridge.
python "%~dp0procoder_hook.py" %*
exit /b %ERRORLEVEL%
