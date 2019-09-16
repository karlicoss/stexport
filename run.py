#!/usr/bin/env python3
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


# FILTER = 'default'
FILTER = '!LVBj2-meNpvsiW3UvI3lD('
# check it out here https://api.stackexchange.com/docs/read-filter#filters=!SnL4e6G*07of2S.ynb&filter=default&run=true
# TODO eh, better make it explicit with 'filter' api call https://api.stackexchange.com/docs/create-filter
# private filters: answer.{accepted, downvoted, upvoted}; comment.upvoted . wonder why, accepted is clearly visible on the website..
#


from typing import List

from stackapi import StackAPI

from ssecrets import *

# api = StackAPI('stackoverflow', key=key, access_token=access_token)
# right. not sure if there is any benefit in using authorised user? not that much data is private

def run(user_id: str, apis: List[str]):
    # TODO FIXME use apis
    # TODO use sites? https://api.stackexchange.com/docs/sites
    api = StackAPI('stackoverflow')
    data = {}
    # TODO eh, don't think I need rest of paginated stuff??
    for ep in ENDPOINTS:
        # TODO eh, gonna end up with weird 
        data[ep] = api.fetch(
            endpoint=ep.format(ids=user_id, id=user_id),
            filter=FILTER,
        )['items']
    import json
    import sys
    json.dump(data, sys.stdout, ensure_ascii=False, indent=1)


def main():
    run(
        user_id=user_id,
        apis=['stackoverflow'],
    )

if __name__ == '__main__':
    main()
