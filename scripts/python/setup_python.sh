#!/bin/bash

# change to local home directory and check that we can user the ec2-user
echo "User:"
whoami
echo "user: "
sudo -u ec2-user bash -c "whoami"
cd ~/
echo "Current Dir:"
pwd 

# update instance
sudo yum check-update
sudo yum install screen -y
sudo yum install git-all -y


# need to run in subshell so we can use the ec2-user

sudo -u ec2-user bash <<"EOF"
# Download and install minconda
wget 'https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh' -O ~/miniconda.sh
cd ~
sudo chmod a+rwx miniconda.sh
~/miniconda.sh -b -p /home/ec2-user/miniconda
# create and activate the environment
export PATH="/home/ec2-user/miniconda/bin:$PATH"
rm miniconda.sh
conda create -n newenviron --yes python=3.5 pip scipy pandas numpy psycopg2 sphinx pylint
source activate newenviron

# add to bashrc
cd ~
# backup of bashrc
cp .bashrc .bashrc.bkup
echo export\ PATH="/home/ec2-user/miniconda/bin:\$PATH" >> .bashrc


# pull down whatever files you wish to run - add code here 
# the following is shown as an example where we
# wish to run luigi scripts

cd ~
mkdir repos
cd repos
git clone https://github.com/ejokeeffe/boiler_deploy.git
cd boiler_deploy/scripts/luigi
sudo chmod a+rwx setup_luigi.sh
bash setup_luigi.sh
cd ~/repos/boiler_deploy/examples/luigi_tasks
sudo chmod a+rwx setup_examples.sh
bash setup_examples.sh

EOF
