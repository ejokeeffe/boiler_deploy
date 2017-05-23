#!/bin/bash

# install luigi and dependencies
# before running ensure your environment is activated
pip install luigi
pip install sqlalchemy
pip install boto

# add environment variables
cd ~
cp .bashrc .bashrc.bkup.luigiinstall
echo export\ PYTHONPATH="/home/ec2-user/repos/boiler_deploy/examples/luigi_tasks:/home/ec2-user/tasks:\$PYTHONPATH" >> .bashrc

#copy the config across
cp ~/repos/boiler_deploy/scripts/luigi/luigi.cfg ~/luigi.cfg

# copy boto file for accessing s3
cp ~/repos/boiler_deploy/scripts/luigi/.boto ~/.boto

# add the environment variable for the location of this file
echo export\ LUIGI_CONFIG_PATH="/home/ec2-user/luigi.cfg" >> .bashrc

# set up folder to store history
mkdir ~/luigi_logger