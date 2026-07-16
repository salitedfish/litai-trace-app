#!/usr/bin/env bash

venv_switch='on'

os_name=$(uname)
if [[ "$os_name" == 'Linux' ]]; then
   get_path=readlink
elif [[ "$os_name" == 'Darwin' ]]; then
   get_path=greadlink
fi

work_dir=$(dirname $(dirname $($get_path -f $0)))
for file in ${work_dir}/src/*
do [ -d $file ] && { app_name=${file##*/}; break; } done

cd $work_dir

major=$(python -c 'import sys; print(sys.version_info.major)')
minor=$(python -c 'import sys; print(sys.version_info.minor)')
if [[ $major -ne 3 || $minor -ne 6 ]]; then
    echo "python version error, python3.6 is required"
    exit -1
fi

if [ ! -f .already_package ]; then
    echo "can not install without packaging"
    exit -1
fi

if [ ! -d  ~/.pip ]; then
    mkdir ~/.pip
    touch ~/.pip/pip.conf
    echo '[global]' >> ~/.pip/pip.conf
    echo 'index-url = https://pypi.tuna.tsinghua.edu.cn/simple' >> ~/.pip/pip.conf
fi

if [[ "$venv_switch" == 'on' ]]; then
    [ -d env ] && rm -rf env
    python -m virtualenv env
    if [ $? -ne 0 ]; then
        echo "virtualenv error, installing interrupt"
        exit -1
    fi
    source env/bin/activate
fi

whl_count=$(ls lib | grep -i '^mg_app_framework.*whl$' | wc -l)
if [[ "$whl_count" != 1 ]]; then
    echo "pip install error, mg_app_framework.*whl count != 1"
    exit -1
fi

for item in $(ls lib/*.whl);do
    python -m pip install $item
    if [ $? -ne 0 ]; then
        echo "pip install error, installing interrupt"
        exit -1
    fi
done
for item in $(cat ./lib/requirements.txt);do
    python -m pip install $item
    if [ $? -ne 0 ]; then
        echo "pip install error, installing interrupt"
        exit -1
    fi
done

chmod u+x ./bin/run.sh

cat>${app_name}.service<<EOF
[Unit]
Description=ManuGence ${app_name}

[Service]
Type=simple
User=root
ExecStart=${work_dir}/env/bin/python ${work_dir}/src/run_${app_name}.py product
Restart=always
RestartSec=300
StartLimitInterval=0
RestartPreventExitStatus=143 137 SIGTERM SIGKILL
StandardOutput=null

[Install]
WantedBy=multi-user.target
EOF

cp ${app_name}.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ${app_name}
echo "service created"

touch .already_install
echo 'info: finish'
