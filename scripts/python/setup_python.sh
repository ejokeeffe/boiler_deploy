#!/bin/bash

# change to local home directory and ec2-user
echo "User:"
whoami
sudo su - ec2-user
echo "user: "
whoami
cd ~/
echo "Current Dir:"
pwd 

# update instance
sudo yum check-update
sudo yum install screen -y
sudo yum install git-all -y



# Download and install minconda
wget 'https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh' -O ~/miniconda.sh
cd ~
sudo chmod a+rwx miniconda.sh
sudo -u ec2-user bash $HOME/miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
rm miniconda.sh

# create and activate the environment
conda create -n newenviron --yes python=3.5 pip scipy pandas numpy psycopg2 sphinx pylint
source activate newenviron

# pull down whatever files you wish to run - add code here
cd ~
mkdir repos
cd repos
