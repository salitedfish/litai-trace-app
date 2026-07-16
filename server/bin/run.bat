@echo off
%1 %2
ver|find "5.">nul&&goto :Admin
mshta vbscript:createobject("shell.application").shellexecute("%~s0","goto :Admin","","runas",1)(window.close)&goto :eof
:Admin

set debug_switch=off
set venv_switch=on
cd /d %~dp0 && cd /d ..
set work_dir=%cd%

for /d %%i in (%work_dir%\src\*) do (
    set app_name=%%~ni
    goto break_
)
:break_

echo ###############################33; 选择要执行的操作############################
echo ----------------------1 输入1后回车, 启动服务----------------------
echo ----------------------2 输入2后回车, 关闭服务----------------------
echo ----------------------3 输入3后回车, 重启服务----------------------
echo ----------------------4 输入其他任意字符, 退出程序----------------------
echo.
echo 请选择要执行的操作
set /p num=
if "1"=="%num%" (
    cls
    env\Scripts\activate
    python %work_dir%\src\run_%app_name%.py start
    pause
)

if "2"=="%num%" (
    cls
    env\Scripts\activate
    python %work_dir%\src\run_%app_name%.py stop
    pause
)

if "3"=="%num%" (
    cls
    env\Scripts\activate
    python %work_dir%\src\run_%app_name%.py restart
    pause
)
