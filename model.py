#!/usr/bin/env python3
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Sequence, Any
from glob import glob
from datetime import datetime
import json
import logging

from kython import setup_logzero

import pytz

def get_logger():
    return logging.getLogger('stexport')


class Question(NamedTuple):
    j: Any

    # TODO wonder if could use something like attrs to reduce boilerplate
    # TODO: e.g. generate baseed on namedtuple schema?
    @property
    def title(self) -> str:
        return self.j['title']

    @property
    def tags(self) -> Sequence[str]:
        return self.j['tags']

    @property
    def creation_date(self) -> datetime:
        # all utc https://api.stackexchange.com/docs/dates
        return datetime.fromtimestamp(self.j['creation_date'], tz=pytz.utc)

    @property
    def link(self) -> str:
        return self.j['link']


class SiteModel:
    def __init__(self, j):
        self.j = j

    @property
    def questions(self):
        return self.j['users/{ids}/questions']


class Model:
    def __init__(self, sources: Sequence[Path]):
        # TODO allow passing multiple later to construct the whole model from chunks
        [src] = sources
        self.src  = src
        self.data = json.loads(self.src.read_text())

    def sites(self):
        return list(sorted(self.data.keys()))

    def site_model(self, site: str):
        return SiteModel(self.data[site])


def main():
    logger = get_logger()
    setup_logzero(logger, level=logging.DEBUG)
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=str, required=True)
    p.add_argument('--no-glob', action='store_true')
    args = p.parse_args()

    if '*' in args.source and not args.no_glob:
        sources = glob(args.source)
    else:
        sources = [args.source]

    src = Path(max(sources))

    logger.debug('using %s', src)
    model = Model([src])

    for site in model.sites():
        sm = model.site_model(site)
        qs = sm.questions
        if len(qs) == 0:
            continue
        print(f"At {qs}:")
        for q in qs:
            print(q)



if __name__ == '__main__':
    main()
