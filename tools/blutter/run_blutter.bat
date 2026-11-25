@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
set PATH=C:\Users\daong\Projects\tools\blutter\.venv\Scripts;%PATH%
cd /d C:\Users\daong\Projects\tools\blutter
where cl
python blutter.py C:\Users\daong\Projects\powerbox-multilingual\local\work\lib\arm64-v8a C:\Users\daong\Projects\powerbox-multilingual\local\blutter-arm64 %*
echo BLUTTER_EXIT=%ERRORLEVEL%
