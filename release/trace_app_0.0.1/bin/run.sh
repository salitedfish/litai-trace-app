#!/usr/bin/env bash

os_name=$(uname)
if [[ "$os_name" == 'Linux' ]]; then
   get_path=readlink
elif [[ "$os_name" == 'Darwin' ]]; then
   get_path=greadlink
fi

work_dir=$(dirname $(dirname $($get_path -f $0)))
for file in ${work_dir}/src/*
do [ -d $file ] && { app_name=${file##*/}; break; } done

process_info="ps x | grep src/run_${app_name}.py | grep -v grep"
pid_info="ps x| grep run_${app_name}.py | grep -v grep |awk '{print \$1}'"
pid_file=".${app_name}_pid"

start() {
    cd $work_dir
    if [ ! -f .already_install ]; then
        echo "can not start without installing"
        return 1
    fi
    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        process=$(eval "ps -p ${pid} | sed 1d")
        if [ -n "$process" ]; then
            echo "error: ${app_name}(pid=${pid}) is already running."
            return 1
        else
            rm $pid_file
        fi
    fi
    service=$(eval $process_info)
    if [ -n "$service" ]; then
        echo "info: a running ${app_name} instance exists."
    fi
    systemctl start ${app_name}

    pid=$(eval $pid_info)
    echo $pid > $pid_file
    sleep 1
    pid=$(cat $pid_file)
    process=$(eval "ps -p ${pid} | sed 1d")
    if [ -n "$process" ]; then
    	echo "info: ${app_name}(pid=${pid}) started."
        return 0
    else
        echo "error: ${app_name} starting failed"
	    return 1
    fi
}

stop() {
    cd $work_dir
    service=$(eval $process_info)
    if [ -z "$service" ]; then
    	[ -f $pid_file ] && rm $pid_file
        echo "info: ${app_name} is not running."
        return 1
    else
    	if [ ! -f $pid_file ]; then
            echo "error: $(pwd)/${pid_file} not found, please kill by hand"
	        return 1
    	fi
    fi
    pid=$(cat $pid_file)

    systemctl stop ${app_name}
    sleep 1
    process=$(eval "ps -p ${pid} | sed 1d")
    if [ -z "$process" ]; then
        rm $pid_file
        echo "info: ${app_name}(pid=${pid}) stopped."
        return 0
    fi
    echo "error: ${app_name}(pid=${pid}) stopping failed"
    return 1
}

status() {
    cd $work_dir
    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        process=$(eval "ps -p ${pid} | sed 1d")
        if [ -n "$process" ]; then
            echo "${app_name}(pid=${pid}) is running."
        else
            rm $pid_file
            echo "${app_name}(pid=${pid}) is not running"
        fi
    else
	    echo "${app_name} is not running"
    fi
    return 0
}

debug() {
    service=$(eval $process_info)
    if [ -n "$service" ]; then
        pid=$(eval $pid_info)
        echo "error: ${app_name}(pid=${pid}) is running, please kill by hand"
        return 1
    fi

    source env/bin/activate && python "./src/run_${app_name}.py"
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  status)
    status
    ;;
  debug)
    debug
    ;;
  *)
    echo "usage: run.sh {start|stop|restart|status|debug}"
    exit 1
esac
