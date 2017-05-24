# -*- coding: utf-8 -*-
#
# Extension to https://github.com/spotify/luigi/blob/master/examples/top_artists.py
#
import random
from collections import defaultdict
import os
from luigi import six

import luigi
import luigi.contrib.s3 as luigi_s3
import luigi.contrib.postgres
import boto
from heapq import nlargest

from time import sleep

class StreamsS3(luigi.Task):
    """
    Faked version right now, just generates bogus data.
    """
    date = luigi.DateParameter()
    sleep_seconds = luigi.Parameter()

    def run(self):
        """
        Generates bogus data and writes it into the :py:meth:`~.Streams.output` target.
        """
        sleep(int(self.sleep_seconds))
        with self.output().open('w') as output:
            for _ in range(1000):
                output.write('{} {} {}\n'.format(
                    random.randint(0, 999),
                    random.randint(0, 999),
                    random.randint(0, 999)))

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file in the s3 file system.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi_s3.S3Target("s3:{0}{1}".format(
            os.environ["LUIGIS3_EXAMPLES"],
            self.date.strftime('streams_%Y_%m_%d_faked.tsv')))


class AggregateArtistsS3(luigi.Task):
    """
    This task runs over the target data returned by :py:meth:`~/.Streams.output` and
    writes the result into its :py:meth:`~.AggregateArtists.output` target (local file).
    """

    date_interval = luigi.DateIntervalParameter()
    sleep_seconds = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        s3_string="s3:{0}{1}".format(
            os.environ["LUIGIS3_EXAMPLES"],
            "artist_streams_{}.tsv".format(self.date_interval))
        return luigi_s3.S3Target(s3_string)

    def requires(self):
        return [StreamsS3(date,self.sleep_seconds) for date in self.date_interval]

    def run(self):
        artist_count = defaultdict(int)

        for t in self.input():
            with t.open('r') as in_file:
                for line in in_file:
                    _, artist, track = line.strip().split()
                    artist_count[artist] += 1

        with self.output().open('w') as out_file:
            for artist, count in six.iteritems(artist_count):
                out_file.write('{}\t{}\n'.format(artist, count))

class Top10ArtistsS3(luigi.Task):

    date_interval = luigi.DateIntervalParameter()
    sleep_seconds = luigi.Parameter()

    def requires(self):
        return AggregateArtistsS3(self.date_interval,self.sleep_seconds)

    def output(self):
        s3_string="s3:{0}{1}".format(
            os.environ["LUIGIS3_EXAMPLES"],
            "data/top_artists_{}.tsv".format(self.date_interval))
        return luigi_s3.S3Target(s3_string)

    def run(self):
        top_10 = nlargest(10, self._input_iterator())
        with self.output().open('w') as out_file:
            for streams, artist in top_10:
                out_line = '\t'.join([
                    str(self.date_interval.date_a),
                    str(self.date_interval.date_b),
                    artist,
                    str(streams)
                ])
                out_file.write((out_line + '\n'))

    def _input_iterator(self):
        with self.input().open('r') as in_file:
            for line in in_file:
                artist, streams = line.strip().split()
                yield int(streams), artist

class ArtistS3ToDatabase(luigi.contrib.postgres.CopyToTable):
    """
    This task runs a :py:class:`luigi.postgres.CopyToTable` task
    over the target data returned by :py:meth:`~/.Top10Artists.output` and
    writes the result into its :py:meth:`~.ArtistToplistToDatabase.output` target which,
    by default, is :py:class:`luigi.postgres.PostgresTarget` (a table in PostgreSQL).
    This class uses :py:meth:`luigi.postgres.CopyToTable.run` and :py:meth:`luigi.postgres.CopyToTable.output`.
    """

    date_interval = luigi.DateIntervalParameter()
    sleep_seconds = luigi.Parameter()

    host = os.environ["LUIGI_DBHOST"]
    database = os.environ["LUIGI_DBDATABASE"]
    user = os.environ["LUIGI_DBUSER"]
    password = os.environ["LUIGI_DBPASS"]
    table = "artist_streams"

    columns = [("date_from", "DATE"),
               ("date_to", "DATE"),
               ("artist", "TEXT"),
               ("streams", "INT")]

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.Top10Artists`
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return Top10ArtistsS3(self.date_interval,self.sleep_seconds)