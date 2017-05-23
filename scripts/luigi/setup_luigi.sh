#!/bin/bash

# install luigi
pip install luigi

# add environment variables
cp .bashrc .bashrc.bkup.luigiinstall
echo export\ PATH="/home/ec2-user/miniconda/bin:\$PATH" >> .bashrc
echo export\ PYTHONPATH="/home/ec2-user/repos/boiler_deploy/examples/luigi_tasks:\$PYTHONPATH" >> .bashrc