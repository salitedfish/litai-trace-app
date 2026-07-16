#!/usr/bin/env bash

app_type=''
version='0.0.1'

os_name=$(uname)
if [[ "$os_name" == 'Linux' ]]; then
   get_path=readlink
elif [[ "$os_name" == 'Darwin' ]]; then
   echo "Darwin平台greadlink需要提前安装\n"
   echo "通过 brew install coreutils\n"
   get_path=greadlink
fi

work_dir=$(dirname $(dirname $($get_path -f $0)))

if [[ -d $work_dir/server ]]; then
    src_dir=$work_dir/server/src
else
    src_dir=$work_dir/src
fi

[[ -d "$src_dir/__pycache__" ]] && rm -rf "$src_dir/__pycache__"

module_dir=$(find $src_dir -mindepth 1 -maxdepth 1 -type d)

for dir in $module_dir
do
    if [[ -f $dir/config_product.py ]]; then
        module_dir=$dir
        break
    fi
done

if [[ -f $module_dir/config_product.py ]]; then
    app_type_line=$(grep "AppType." $module_dir/config_product.py)
    if [ $? -ne 0 ]; then
        echo "获取app类型失败"
        exit -1
    fi
else
    echo '获取app类型失败, 退出打包脚本'
    exit -1
fi

if [[ $app_type_line == *"AppType.user"* ]];then
    if [[ -f $work_dir/web/quasar.conf.js ]];then
        app_type='user'
    elif [[ -f $work_dir/web/vue.config.js ]];then
        app_type='module'
    fi
fi

for file in $src_dir/*
do
    [ -d $file ] && { app_name=${file##*/}; break; }
done

echo "$app_name release version is $version"

cd $work_dir

package_dir="$work_dir/release/${app_name}_${version}"
rm -rf $package_dir
mkdir $package_dir

if [[ "$app_type" == 'user' || "$app_type" == 'module' ]]; then
    cp -a ./server/bin ./server/lib ./server/src $package_dir
else
    cp -a bin lib src $package_dir
fi

mkdir "${package_dir}/log"
[ -d "${package_dir}/src/${app_name}/__pycache__" ] && rm -rf "${package_dir}/src/${app_name}/__pycache__"
rm -rf "${package_dir}/src/${app_name}/config.py"
mv "${package_dir}/src/${app_name}/config_product.py" "${package_dir}/src/${app_name}/config.py"

cd $package_dir
touch .already_package
touch .appid
echo '0-0-0-0-0' > .appid

touch .git_info
git rev-parse HEAD > .git_info 2>/dev/null || echo "no-git" > .git_info

cd $(dirname $package_dir)
tar zvcf "${app_name}_${version}.tar.gz" "${app_name}_${version}"

cd $work_dir
rm -rf $package_dir

echo "finish"
