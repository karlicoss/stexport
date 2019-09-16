#!/usr/bin/env python3
from typing import List

# https://stackapi.readthedocs.io/en/latest/user/advanced.html?highlight=key#send-data-via-the-api

# TODO right. not sure if there is any benefit in using authorised user? not that much data is private


from stackapi import StackAPI

from ssecrets import *


# see https://api.stackexchange.com/docs
ENDPOINTS = [
    "users/{ids}",
    "users/{ids}/answers",
    "users/{ids}/badges",
    "users/{ids}/comments",
    "users/{ids}/favorites",
    "users/{ids}/mentioned",
    "users/{id}/network-activity",
    "users/{id}/notifications",
    "users/{ids}/posts",
    "users/{id}/privileges",
    "users/{ids}/questions",
    # users/{ids}/questions/featured # TODO not ure if necessary?
    # users/{ids}/questions/no-answers
    # users/{ids}/questions/unaccepted
    # users/{ids}/questions/unanswered
    "users/{ids}/reputation",
    "users/{ids}/reputation-history",
    # users/{id}/reputation-history/full
    "users/{ids}/suggested-edits",
    "users/{ids}/tags",
    # users/{id}/tags/{tags}/top-answers
    # users/{id}/tags/{tags}/top-questions
    "users/{ids}/timeline",
    "users/{id}/top-answer-tags",
    "users/{id}/top-question-tags",
    "users/{id}/top-tags",
    "users/{id}/write-permissions",
    # users/{id}/inbox
    # users/{id}/inbox/unread
]


# check it out here https://api.stackexchange.com/docs/read-filter#filters=!SnL4e6G*07of2S.ynb&filter=default&run=true
FILTER = '!SnL4e6G*07of2S.ynb'
# FILTER = 'default'

def run(user_id: str, apis: List[str]):
    # api = StackAPI('stackoverflow')
    api = StackAPI('stackoverflow', key=key, access_token=access_token)
    data = {}
    # TODO eh, don't think I need rest of paginated stuff??
    for ep in ENDPOINTS[:2]:
        ep = ep.format(ids=user_id, id=user_id)
        name = ep.split('/')[-1]
        data[name] = api.fetch(
            ep,
            # TODO mm. withbody doesn't add body_markdown, where at it's somewhat more useful...
            filter=FILTER,
        )['items']
    import json
    import sys
    json.dump(data, sys.stdout, ensure_ascii=False, indent=1)
    # TODO shit, looks like it only gives away answer ids?


def main():
    run(
        user_id=user_id,
        apis=['stackoverflow'],
    )

if __name__ == '__main__':
    main()
