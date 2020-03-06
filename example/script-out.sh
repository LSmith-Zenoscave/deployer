#!/bin/bash

function command_1cd9557a-d7c4-42f8-96b8-e6852beefcb0() {

    echo 'run pwd'
    pwd
    exit_code=$?

    if [[ ${exit_code} = 0 ]] ; then
        command_bb17fc06-a6b7-4fa5-98ed-b86958262adb # check for updates
    fi
}

function command_bb17fc06-a6b7-4fa5-98ed-b86958262adb() {

    echo 'check for updates'
    sudo apt update && sudo apt upgrade
    exit_code=$?

    if [[ ${exit_code} = 0 ]] ; then
        command_d813b687-c74a-45bf-87cd-608269185b4a # save dpkg
    fi

    if [[ ${exit_code} = 1 ]] ; then
        command_8c942ccb-dae1-4bec-bb56-efc9ad50f4c3 # Warn of failure
    fi
}

function command_d813b687-c74a-45bf-87cd-608269185b4a() {

    echo 'save dpkg'
    dpkg -l | awk '/ii/ { print $2 }' | tee packages.txt
    exit_code=$?

    if [[ ${exit_code} = 0 ]] ; then
        command_1c9cd7b3-df39-4e5d-892e-9a4d5379cb07 # list info from dpkg
    fi
}

function command_1c9cd7b3-df39-4e5d-892e-9a4d5379cb07() {

    echo 'list info from dpkg'
    dpkg -l
    exit_code=$?
}

function command_8c942ccb-dae1-4bec-bb56-efc9ad50f4c3() {

    echo 'Warn of failure'
    echo 'Failed to update apt or upgrade packages'
	exit 1
    exit_code=$?
}

function command_None() {
    echo "This script is not finished."
    exit 1
}

command_1cd9557a-d7c4-42f8-96b8-e6852beefcb0
echo "Done: ${exit_code}"
exit ${exit_code}
