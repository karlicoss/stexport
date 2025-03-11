from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from .exporthelpers.dal_helper import Json
from .exporthelpers.logging_helper import make_logger

logger = make_logger(__name__)


class Question(NamedTuple):
    j: Json

    # TODO wonder if could use something like attrs to reduce boilerplate
    # TODO: e.g. generate baseed on namedtuple schema?
    @property
    def title(self) -> str:
        return self.j['title']

    @property
    def body_markdown(self) -> str:
        return self.j['body_markdown']

    @property
    def tags(self) -> Sequence[str]:
        return self.j['tags']

    @property
    def creation_date(self) -> datetime:
        # all utc https://api.stackexchange.com/docs/dates
        return datetime.fromtimestamp(self.j['creation_date'], tz=timezone.utc)

    @property
    def link(self) -> str:
        return self.j['link']


class SiteDAL(NamedTuple):
    j: Json

    @property
    def questions(self) -> Iterable[Question]:
        return sorted(map(Question, self.j['users/{ids}/questions']), key=lambda q: q.creation_date)


class DAL:
    def __init__(self, sources: Sequence[Path]) -> None:
        # TODO later, reconstruct from chunks?
        self.src = max(sorted(sources))
        self.data = json.loads(self.src.read_text())

    def sites(self) -> Sequence[str]:
        return sorted(self.data.keys())

    def site_dal(self, site: str) -> SiteDAL:
        return SiteDAL(self.data[site])


def demo(dal: DAL) -> None:
    for site in dal.sites():
        sm = dal.site_dal(site)
        qs = list(sm.questions)
        if len(qs) == 0:
            continue
        print(f"At {qs}:")
        for q in qs:
            print(q)


def main() -> None:
    from .exporthelpers import dal_helper
    dal_helper.main(DAL=DAL, demo=demo)


if __name__ == '__main__':
    main()
