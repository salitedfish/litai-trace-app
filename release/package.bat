@echo off
set version=0.0.1
set app_type=0
cd /d %~dp0 && cd /d ..
set work_dir=%cd%
if exist %work_dir%\server (
    set src_dir=%work_dir%\server\src
) else (
    set src_dir=%work_dir%\src
)

if exist %src_dir%\__pycache__ (
    rd /s/q %src_dir%\__pycache__
)

if not exist %src_dir% (
    echo 目录%src_dir%不存在
    pause
    exit -1
)

for /d %%i in (%src_dir%\*) do (
    if exist %%i\config_product.py (
        set app_name=%%~ni
        set module_dir=%%i
        goto break_
    ) else (
        echo 获取app名称失败, 退出打包脚本
        pause
        exit -1
    )
)
:break_
find "AppType." %module_dir%\config_product.py > null
if %errorlevel%==0 (
    if exist %work_dir%\web\quasar.conf.js (
        set app_type=1
    ) else if exist %work_dir%\web\vue.config.js (
        set app_type=2
    )
) else (
    echo 获取app类型失败, 退出打包脚本
    pause
    exit -1
)
set package_dir=%work_dir%\release\%app_name%_%version%
rd /s/q %package_dir%
md %package_dir%
md %package_dir%\log
if %app_type%==0 (
    xcopy /f /e /c /y %work_dir%\bin  %package_dir%\bin\
    xcopy /f /e /c /y %work_dir%\lib  %package_dir%\lib\
    xcopy /f /e /c /y %work_dir%\src  %package_dir%\src\
) else (
    xcopy /f /e /c /y %work_dir%\server\bin  %package_dir%\bin\
    xcopy /f /e /c /y %work_dir%\server\lib  %package_dir%\lib\
    xcopy /f /e /c /y %work_dir%\server\src  %package_dir%\src\
)

if exist %package_dir%\src\%app_name%\__pycache__ (
    rd /s/q %package_dir%\src\%app_name%\__pycache__
)
del /s /q /f %package_dir%\src\%app_name%\config.py
ren %package_dir%\src\%app_name%\config_product.py config.py
echo already_package > %package_dir%\.already_package
echo 0-0-0-0-0 > %package_dir%\.appid
cd /d %work_dir%\release
echo %cd%
call tar -zcvf %app_name%_%version%.tar.gz %app_name%_%version%
rd /s/q %package_dir%
echo finish
pause
