from __future__ import annotations

# see https://api.stackexchange.com/docs
ENDPOINTS = [
    "users/{ids}",
    "users/{ids}/answers",
    "users/{ids}/badges",
    "users/{ids}/comments",
    "users/{ids}/favorites",
    "users/{ids}/mentioned",

    ##  these don't take 'site' parameter..
    # "users/{id}/network-activity",
    # "users/{id}/notifications",
    ##

    "users/{ids}/posts",
    "users/{id}/privileges",
    "users/{ids}/questions",

    ## these overlap with 'questions'
    # users/{ids}/questions/featured
    # users/{ids}/questions/no-answers
    # users/{ids}/questions/unaccepted
    # users/{ids}/questions/unanswered
    ##


    "users/{ids}/reputation",
    "users/{ids}/reputation-history",

    ## this needs auth token
    # users/{id}/reputation-history/full
    ##

    "users/{ids}/suggested-edits",
    "users/{ids}/tags",

    ## these overlap with 'tags'
    # users/{id}/tags/{tags}/top-answers
    # users/{id}/tags/{tags}/top-questions
    ##

    "users/{ids}/timeline",
    "users/{id}/top-answer-tags",
    "users/{id}/top-question-tags",
    "users/{id}/top-tags",

    ## TODO err, this was often resulting in internal server error...
    # "users/{id}/write-permissions",
    ##

    ## these need auth token, not sure how useful are they
    # users/{id}/inbox
    # users/{id}/inbox/unread
    ##
]


# FILTER = 'default'
FILTER = '!LVBj2(M0Wr1s_VedzkH(VG'
# check it out here https://api.stackexchange.com/docs/read-filter#filters=!SnL4e6G*07of2S.ynb&filter=default&run=true
# TODO eh, better make it explicit with 'filter' api call https://api.stackexchange.com/docs/create-filter
# private filters: answer.{accepted, downvoted, upvoted}; comment.upvoted . wonder why, accepted is clearly visible on the website..
#


import argparse
import json
import logging

from stackapi import StackAPI, StackAPIError  # type: ignore[import-untyped]
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exporthelpers.export_helper import Json
from .exporthelpers.logging_helper import make_logger

logger = make_logger(__name__)

# few wrappers to make less api calls to 'sites' endpoint..
from functools import lru_cache


@lru_cache
def _get_api(**kwargs):
    # TODO FIXME max_page documentation is wrong, it's 5 by default?
    # kinda_infinity = 1_000_000
    # api = StackAPI('stackoverflow', max_pages=kinda_infinity)

    api = StackAPI('stackoverflow', **kwargs)
    # right. not sure if there is any benefit in using authorised user? not that much data is private

    api._name = None
    api._api_key = None
    return api

@lru_cache
def get_all_sites(api) -> dict[str, str]:
    """Returns all the StackExchange sites as a dict, api_site_parameter -> name"""
    # hacky way to get everything..
    res = api.fetch('sites')
    return {s['api_site_parameter']: s['name'] for s in res['items']}


@lru_cache
def get_user_sites(api) -> dict[str, str]:
    """
    Returns all the associated sites for the /me user. The /me user is the one who's
    access_token we're authorized with (so it's required)
    Returned as a dict. api_site_parameter -> name
    """
    # Get all the associated site names, just like from the output of get_all_sites
    res = api.fetch('me/associated')
    # Remove the ' Stack Exchange' at the end of the names to make them match
    associate_site_names: list[str] = [s['site_name'].replace(' Stack Exchange', '') for s in res['items']]

    # Invert get_all_sites to map name to api_site_parameter
    all_sites_inv = {v: k for k, v in get_all_sites(api).items()}
    # Return all of me's associated sites with the same api_site_parameter
    # mapping as get_all_sites
    # This isn't a 1-to-1 mapping unfortunately... :c
    user_sites_inv = {n: all_sites_inv[n] if n in all_sites_inv.keys() else None for n in associate_site_names}

    # Notify of missing mappings
    for k, v in user_sites_inv.items():
        if v is None:
            logger.warning(f'Missing site mapping for {k}, didnt match all_sites format')

    # Flip for return to be like get_all_sites, filter out missings
    return {v: k for k, v in user_sites_inv.items() if v is not None}


class RetryMe(Exception):
    pass


@retry(
    retry=retry_if_exception_type(RetryMe),
    wait=wait_exponential(max=10),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def fetch_with_retry(api, *args, **kwargs):
    try:
        return api.fetch(*args, **kwargs)
    except StackAPIError as e:
        if "Remote end closed connection without response" in e.message:
            # ugh, not sure why is it happening, but seems trainsient
            raise RetryMe from e
        if "Expecting value: line 1 column 1 (char 0)" in e.message:
            # weird, also happens for no good reason occasionally?
            raise RetryMe from e
        if "unusual number of requests coming from this IP address" in e.message:
            # happens sometimes close to the rate limit??
            # also weird error, some sort of HTML page...
            # typically takes like 30 seconds to pass... so retry logic manages from like 5th attempt..
            raise RetryMe from e
        raise e


class Exporter:
    def __init__(self,  **kwargs) -> None:
        self.api_params = kwargs
        self.api = _get_api(**self.api_params)

    def get_site_api(self, site: str):
        api = _get_api(**self.api_params)
        sites = get_all_sites(api)
        api._name = sites[site]
        api._api_key = site
        return api

    def export_site(self, site: str) -> Json:
        logger.info('exporting %s: started...', site)
        api = self.get_site_api(site)

        ur = fetch_with_retry(
            api,
            endpoint='me',
            filter=FILTER,
        )
        items = ur['items']
        if len(items) == 0:
            # todo not sure if need to warn? maybe only in --user-sites/--site mode
            return {}
        [item] = items
        user_id = item['user_id']

        data = {}
        for ep in ENDPOINTS:
            logger.info('exporting %s: %s', site, ep)
            # TODO ugh. still not sure about using weird patterns as dictionary keys...
            r = fetch_with_retry(
                api,
                endpoint=ep.format(ids=user_id, id=user_id),
                filter=FILTER,
            )
            data[ep] = r['items']
        return data


    def export_json(self, sites: list[str]) -> Json:
        """
        sites: None means all of them
        """
        all_data = {}
        for site in sites:
            all_data[site] = self.export_site(site=site)
        return all_data


def make_parser() -> argparse.ArgumentParser:
    from .exporthelpers.export_helper import Parser, setup_parser
    parser = Parser('Export your personal Stackexchange data')
    setup_parser(
        parser=parser,
        params=['key', 'access_token'],
    )
    parser.add_argument('--user-id', type=str, help='DEPRECATED (key/token is enough, option is only for backwards compatibility)')
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--all-sites', action='store_true')
    g.add_argument('--user-sites', action='store_true')
    g.add_argument('--site', action='append')
    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    params = args.params
    dumper = args.dumper

    _UID = 'user_id'
    _uid = getattr(args, _UID)
    if _uid is not None:
        import warnings
        warnings.warn(f"'{_UID}' is deprecated, ther is no need to pass it anymore. See https://github.com/karlicoss/stexport/issues/5")

    generalApi = _get_api(**params) #API for general queries, not on a site
    exporter = Exporter(**params)

    sites = args.site
    if args.all_sites:
        sites = sorted(get_all_sites(generalApi).keys()) # sort for determinism
    elif args.user_sites:
        sites = sorted(get_user_sites(generalApi).keys())

    logger.info('exporting %s', sites)

    j = exporter.export_json(sites=sites)

    js = json.dumps(j, ensure_ascii=False, indent=1)
    dumper(js)


if __name__ == '__main__':
    main()
