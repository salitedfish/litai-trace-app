@echo off
setlocal enabledelayedexpansion

REM Parse command line arguments
set force_rebuild=0
if "%1"=="--force" set force_rebuild=1
if "%1"=="-f" set force_rebuild=1

echo ========================================
echo Ultimate Package Script v1.0
echo Reliable source change detection
echo Usage: package_ultimate.bat [--force]
echo ========================================

set version=0.0.1
set app_type=0
cd /d %~dp0 && cd /d ..
set work_dir=%cd%

REM Get source directory
if exist %work_dir%\server (
    set src_dir=%work_dir%\server\src
) else (
    set src_dir=%work_dir%\src
)

REM Clean Python cache
if exist %src_dir%\__pycache__ (
    rd /s/q %src_dir%\__pycache__
)

if not exist %src_dir% (
    echo ERROR: Source directory %src_dir% does not exist
    exit /b 1
)

REM Get app name and type
for /d %%i in (%src_dir%\*) do (
    if exist %%i\config_product.py (
        set app_name=%%~ni
        set module_dir=%%i
        goto found_app
    )
)
echo ERROR: config_product.py file not found
exit /b 1

:found_app
find "AppType." %module_dir%\config_product.py > nul
if %errorlevel%==0 (
    if exist %work_dir%\web\quasar.conf.js (
        set app_type=1
    ) else if exist %work_dir%\web\vue.config.js (
        set app_type=2
    ) else if exist %work_dir%\web\vite.config.ts (
        set app_type=3
    ) else if exist %work_dir%\web\vite.config.js (
        set app_type=3
    )
) else (
    echo ERROR: AppType not found in config_product.py
    exit /b 1
)

echo App Name: %app_name%
echo App Type: %app_type%

REM Create package directory
set package_dir=%work_dir%\release\%app_name%_%version%
if exist %package_dir% rd /s/q %package_dir%
md %package_dir%
md %package_dir%\log

REM Copy backend files
echo Copying backend files...
if %app_type%==0 (
    xcopy /f /e /c /y %work_dir%\bin  %package_dir%\bin\ >nul
    xcopy /f /e /c /y %work_dir%\lib  %package_dir%\lib\ >nul
    xcopy /f /e /c /y %work_dir%\src  %package_dir%\src\ >nul
) else (
    xcopy /f /e /c /y %work_dir%\server\bin  %package_dir%\bin\ >nul
    xcopy /f /e /c /y %work_dir%\server\lib  %package_dir%\lib\ >nul
    xcopy /f /e /c /y %work_dir%\server\src  %package_dir%\src\ >nul
    md %package_dir%\static

    REM Handle frontend
    cd /d %work_dir%\web
    call :handle_frontend

    if not exist dist (
        echo ERROR: Frontend build failed, dist directory not found
        exit /b 1
    )

    echo Copying frontend files...
    xcopy /f /e /c /y dist  %package_dir%\static\dist\ >nul
)

REM Post processing
if exist %package_dir%\src\%app_name%\__pycache__ (
    rd /s/q %package_dir%\src\%app_name%\__pycache__
)
del /s /q /f %package_dir%\src\%app_name%\config.py >nul 2>&1
ren %package_dir%\src\%app_name%\config_product.py config.py
echo already_package > %package_dir%\.already_package
echo 0-0-0-0-0 > %package_dir%\.appid

REM Create archive
cd /d %work_dir%\release
echo Creating archive...
call tar -zcf %app_name%_%version%.tar.gz %app_name%_%version% >nul 2>&1
rd /s/q %package_dir%

echo ========================================
echo Package completed: %app_name%_%version%.tar.gz
echo ========================================
REM pause removed
goto :eof

REM ========================================
REM Handle frontend build
REM ========================================
:handle_frontend
echo Checking frontend status...

REM Force rebuild mode
if %force_rebuild%==1 (
    echo [MODE] Force rebuild enabled
    call :build_frontend
    goto :eof
)

REM Check if basic files exist
if not exist package.json (
    echo [CHECK] package.json missing, building frontend
    call :build_frontend
    goto :eof
)

if not exist node_modules (
    echo [CHECK] node_modules missing, building frontend
    call :build_frontend
    goto :eof
)

if not exist dist (
    echo [CHECK] dist missing, building frontend
    call :build_frontend
    goto :eof
)

REM Check source signature
call :check_source_signature
if !signature_changed!==1 (
    echo [CHECK] Source signature changed, rebuilding frontend
    call :build_frontend
    goto :eof
)

echo [SKIP] Source signature unchanged, using existing build
echo [INFO] No source changes detected since last build
echo [TIP] Use --force to rebuild anyway

goto :eof

REM ========================================
REM Check source signature (simple and reliable)
REM ========================================
:check_source_signature
set signature_changed=0
set signature_file=.source_signature

REM Calculate current signature
call :calculate_signature current_sig

REM If no signature file exists, need to build
if not exist %signature_file% (
    echo [CHECK] No signature file found
    set signature_changed=1
    goto :eof
)

REM Read stored signature and trim whitespace
set /p stored_sig=<%signature_file% 2>nul
if "%stored_sig%"=="" set stored_sig=none

REM Trim whitespace from both signatures
set current_sig=%current_sig: =%
set stored_sig=%stored_sig: =%

REM Compare signatures
if not "%current_sig%"=="%stored_sig%" (
    echo [CHECK] Signature changed
    echo [DEBUG] Old: [%stored_sig%]
    echo [DEBUG] New: [%current_sig%]
    set signature_changed=1
) else (
    echo [CHECK] Signature unchanged
)

goto :eof

REM ========================================
REM Calculate simple signature based on file sizes
REM ========================================
:calculate_signature
set sig_result=

REM Get package.json size
if exist package.json (
    for %%f in (package.json) do set sig_result=!sig_result!pkg:%%~zf;
)

REM Get vue/vite config size
if exist vue.config.js (
    for %%f in (vue.config.js) do set sig_result=!sig_result!vue:%%~zf;
)
if exist vite.config.ts (
    for %%f in (vite.config.ts) do set sig_result=!sig_result!vite:%%~zf;
)
if exist vite.config.js (
    for %%f in (vite.config.js) do set sig_result=!sig_result!vite:%%~zf;
)

REM Get yarn.lock size
if exist yarn.lock (
    for %%f in (yarn.lock) do set sig_result=!sig_result!yarn:%%~zf;
)

REM Count and sum source files
set src_count=0
set src_size=0

if exist src (
    for /r src %%f in (*.vue *.js *.ts *.jsx *.tsx *.css *.scss *.sass *.less *.html) do (
        set /a src_count+=1
        set /a src_size+=%%~zf
    )
)

REM Count and sum public files
set pub_count=0
set pub_size=0

if exist public (
    for /r public %%f in (*.*) do (
        set /a pub_count+=1
        set /a pub_size+=%%~zf
    )
)

set sig_result=!sig_result!src:!src_count!:!src_size!;pub:!pub_count!:!pub_size!

REM Return the signature
set %1=!sig_result!
goto :eof

REM ========================================
REM Build frontend
REM ========================================
:build_frontend
echo Building frontend...

REM Check if need to install dependencies
if not exist node_modules (
    echo Installing dependencies...
    call npm install yarn -g >nul 2>&1
    call yarn config set registry https://registry.npm.taobao.org >nul 2>&1
    call yarn install

    if not %errorlevel%==0 (
        echo ERROR: Dependencies installation failed
        exit /b 1
    )
) else (
    echo Dependencies already installed, skipping
)

REM Clean and build
if exist dist rd /s/q dist

echo Compiling frontend code...
if %app_type%==2 (
    call npm run app_lib
) else if %app_type%==3 (
    call npm run build
) else (
    call npm run app_build
)

if not %errorlevel%==0 (
    echo ERROR: Frontend build failed
    REM pause removed
    exit -1
)

REM Store current signature
call :calculate_signature new_sig
echo !new_sig! > .source_signature
echo Frontend build completed successfully

goto :eof
