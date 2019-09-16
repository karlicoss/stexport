# https://stackapi.readthedocs.io/en/latest/user/advanced.html?highlight=key#send-data-via-the-api

# TODO right. not sure if there is any benefit in using authorised user? not that much data is private
# SITE = StackAPI('stackoverflow', key=key, access_token=access_token)


from stackapi import StackAPI
SITE = StackAPI('stackoverflow')
SITE.fetch('comments')
SITE.fetch('me/comments')
SITE.fetch('me/comments')
SITE.fetch('users/706389/posts')
