# -*- coding: utf-8 -*-

import hashlib
import inspect
import sys
from maldonne.objects.malfeedentry import MalFeedEntry


class MalFeed(object):
    def __init__(self, malfeedconfig):
        self.name = malfeedconfig.get('name', None)
        self.title = malfeedconfig.get('title', '')
        self.description = malfeedconfig.get('description', '')
        self.publisher = malfeedconfig.get('publisher', '')
        self.rights = malfeedconfig.get('rights', '')

        self.engine_name = malfeedconfig.get('engine', None)
        self.feedurl = malfeedconfig.get('feedurl', None)
        self.tags = malfeedconfig.get('tags', '').split(',')
        self.type = malfeedconfig.get('type', None)
        self.use_dns = malfeedconfig.get('use_dns', 0)
        self.use_geoip = malfeedconfig.get('use_geoip', 0)
        self.extended = malfeedconfig.get('extended', 0)

        self.create_date = None
        self.last_update = None
        self.last_status = None

        self.id = hashlib.md5(self.feedurl).hexdigest()

        self.synced = 0
        self.uptodate = 0

        self._entries = []

        if None in [self.name, self.engine_name, self.feedurl]:
            raise Exception("Error: failed to instanciate MalFeed class. "
                            "Verify required parameters in .ini file")

        self._engine = self._load_engine(self.engine_name)

    def update(self):
        self._engine.update()
        self._update_header()
        self._update_entries()

    def _update_header(self):
        fh = self._engine.feed_header
        for hk in fh.keys():
            oattr = getattr(self, hk)
            if oattr is None or len(oattr) == 0:
                setattr(self, hk, fh[hk])

    def _update_entries(self):
        self._entries = []
        for eentry in self._engine.feed_entries:
            eentry.update({'tags': self.tags,
                           'feedurl': self.feedurl,
                           'type': self.type})
            self._entries.append(MalFeedEntry(eentry, self.extended))

    def header(self):
        rh = dict(self.__dict__)
        del rh['_entries']
        del rh['_engine']
        return rh

    def entries(self):
        return self._entries

    def _load_engine(self, engine_name):
        engineobj = None
        engine_path = "maldonne.engines.{0}".format(engine_name)
        __import__(engine_path)
        engine_module = sys.modules[engine_path]
        engine_classes = inspect.getmembers(engine_module, inspect.isclass)

        classname, classproxy = engine_classes.pop()
        if inspect.getmodule(classproxy).__name__.find(engine_path) == 0:
            try:
                engineobj = classproxy(self.feedurl, self.type)
            except Exception as error:
                raise Exception("Cannot create engine, unexpected engine name: {0}".format(error))
        return engineobj

    def __str__(self):
        return str(self.__dict__)
