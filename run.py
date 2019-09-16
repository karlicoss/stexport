#!/usr/bin/env python3
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
FILTER = '!LVBj2-meNpvsiW3UvI3lD('
# check it out here https://api.stackexchange.com/docs/read-filter#filters=!SnL4e6G*07of2S.ynb&filter=default&run=true
# TODO eh, better make it explicit with 'filter' api call https://api.stackexchange.com/docs/create-filter
# private filters: answer.{accepted, downvoted, upvoted}; comment.upvoted . wonder why, accepted is clearly visible on the website..
#


from typing import Dict, List
import logging

from stackapi import StackAPI

from ssecrets import *

def get_logger():
    return logging.getLogger('stexport')


# few wrappers to make less api calls ti 'sites' endpoint..
from functools import lru_cache
@lru_cache()
def get_api():
    # TODO FIXME max_page documentation is wrong, it's 5 by default?
    kinda_infinity = 1_000_000
    # api = StackAPI('stackoverflow', max_pages=kinda_infinity)

    api = StackAPI('stackoverflow', key=key, access_token=access_token)
    # right. not sure if there is any benefit in using authorised user? not that much data is private

    api._name = None
    api._api_key = None
    return api

@lru_cache()
def get_all_sites() -> Dict[str, str]:
    # hacky way to get everything..
    api = get_api()
    res = api.fetch('sites')
    return {s['api_site_parameter']: s['name'] for s in res['items']}


def get_site_api(site: str):
    sites = get_all_sites()
    api = get_api()
    api._name = sites[site]
    api._api_key = site
    return api


def run_one(user_id: str, site: str):
    logger = get_logger()
    logger.info('exporting %s: started...', site)
    api = get_site_api(site)
    data = {}
    for ep in ENDPOINTS:
        # TODO eh, gonna end up with weird
        logger.info('exporting %s: %s', site, ep)
        data[ep] = api.fetch(
            endpoint=ep.format(ids=user_id, id=user_id),
            filter=FILTER,
        )['items']
    return data


def run(user_id: str, sites: List[str]):
    logger = get_logger()
    logger.info('exporting %s', sites)
    all_data = {}
    for site in sites:
        all_data[site] = run_one(user_id, site=site)
    import json
    import sys
    json.dump(all_data, sys.stdout, ensure_ascii=False, indent=1)


def main():
    logging.basicConfig(level=logging.DEBUG)
    sites = get_all_sites()
    run(
        user_id=user_id,
        sites=sites,
    )

if __name__ == '__main__':
    main()
