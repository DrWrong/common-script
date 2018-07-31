#!/bin/sh

if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

function __tantan() {
    systemctl stop  putong*
    systemctl stop  tantan*
    /workspace/tantan-backend-cd/bin/accesspoint-deploy.sh
}

function __putong() {
5    /workspace/backend-cd/bin/app-deploy.sh conf
}


case $@ in
    putong)
        __putong
        ;;
    tantan)
        __tantan
        ;;
    esac
