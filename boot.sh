#!/bin/bash

if (( $EUID != 0 )); then
  echo "You need to have root privileges to run this script."
  echo "Please try again, this time using 'sudo'."
  echo "Exiting."
  exit
fi

apt install -y python3.10-venv gcc python3-dev

if [ -d .venv ]; then
  echo ".venv exists. Continue!"
else
  echo "create Python virtual environment"
  read -p ">>> press [return] to continue ... "
  sudo -u $SUDO_USER python3 -m venv .venv
  sudo -u $SUDO_USER ./.venv/bin/pip install salt==3006.1
fi
