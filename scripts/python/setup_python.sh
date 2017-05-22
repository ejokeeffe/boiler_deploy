#!/bin/bash

# update instance
sudo yum check-update
sudo yum install screen
sudo yum install git-all

# Download and install minconda
wget 'https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh' -O ~/miniconda.sh
sudo chmod a+rwx miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"

# create the environment
conda create -n <environ_name> --yes python=3.5 pip scipy pandas numpy psycopg2 sphinx pylint