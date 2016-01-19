__author__ = 'majidkabir'

from gluon.custom_import import track_changes;

track_changes(True)
# Add all import to this file after this line
from applications.spdpanel.modules.queue.queuemanager import QueueManager

# Setting user language from user profile
if not auth.user is None and not auth.user.lang is None:
    T.force(auth.user.lang)
else:
    T.force(myconf.take('app.default_lang'))

queue_manager = QueueManager()

## Filters for restricting access of user to datas
if auth.is_logged_in():
    if not auth.has_membership('admin'):
        auth.table_group()._common_filter = lambda query: (auth.table_group().group_owner == auth.user_id)
        auth.table_user()._common_filter = lambda query: ((auth.table_user().user_owner == auth.user_id) |
                                                          (auth.table_user().id == auth.user_id))
