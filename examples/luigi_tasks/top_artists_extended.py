import random
from collections import defaultdict
import os
from luigi import six

import luigi
import luigi.contrib.s3 as luigi_s3
import boto

class StreamsS3(luigi.Task):
    """
    Faked version right now, just generates bogus data.
    """
    date = luigi.DateParameter()

    def run(self):
        """
        Generates bogus data and writes it into the :py:meth:`~.Streams.output` target.
        """
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
        return luigi_s3.S3Target("s3://{0}{1}".format(
            os.environ["LUIGIS3_EXAMPLES"],
            self.date.strftime('streams_%Y_%m_%d_faked.tsv')))


class AggregateArtistsS3(luigi.Task):
    """
    This task runs over the target data returned by :py:meth:`~/.Streams.output` and
    writes the result into its :py:meth:`~.AggregateArtists.output` target (local file).
    """

    date_interval = luigi.DateIntervalParameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi_s3.S3Target("s3://{0}{1}".format(
            os.environ["LUIGIS3_EXAMPLES"],
            "artist_streams_{}.tsv".format(self.date_interval)))

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.Streams`
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return [StreamsS3(date) for date in self.date_interval]

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
