#!/bin/bash

# get the example file from http://luigi.readthedocs.io/en/stable/example_top_artists.html
cd ~
mkdir ~/tasks
wget https://raw.githubusercontent.com/spotify/luigi/master/examples/top_artists.py -O ~/tasks/top_artists.py

# add the environment names required
cp .bashrc .bashrc.bkup.luigiexamples





