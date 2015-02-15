#!/usr/bin/env python

from maldonne.objects import MalFeedsCollection, MalFeed
import ConfigParser
import glob
import os


class MalFeedsFactory(object):
    def __init__(self, confdir=None):
        self.feedsconfig = self.load_configs()

    def load_configs(self, confdir=None):
        if confdir is not None:
            base_dir = confdir
        else:
            base_dir = os.path.dirname(os.path.realpath(__file__))

        feedslist = glob.glob("{0}/feeds/*.ini".format(base_dir))
        print feedslist

        try:
            feedsconfig = ConfigParser.ConfigParser()
            feedsconfig.read(feedslist)
        except ConfigParser.ParsingError as e:
            print("error while parsing feeds: {0}".format(e))

        for section in feedsconfig.sections():
            if feedsconfig.getint(section, "enabled") == 0:
                feedsconfig.remove_section(section)
            else:
                feedsconfig.set(section, "name", section)

        return feedsconfig

    def get_feeds(self):
        mfcollection = MalFeedsCollection()

        for section in self.feedsconfig.sections():
            mfsection = dict(self.feedsconfig.items(section))
            mfcollection.add(MalFeed(mfsection))

        return mfcollection


def main():
    feedsfactory = MalFeedsFactory()
    for malfeed in feedsfactory.get_feeds():
        print malfeed.name
        malfeed.update()
        print malfeed.header()
        print "============================"
        for me in malfeed.entries():
            print me.__dict__
            print "----------------------------------"
        print "============================"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
