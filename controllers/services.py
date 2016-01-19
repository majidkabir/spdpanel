from suds.client import Client

try:
    import cPickle as pickle
except:
    import pickle

__author__ = 'majidkabir'

client = Client("http://elogistics.ir/SmsWebserviceImpl?wsdl")


def sendsms():
    rows = db((db.sender.isactive == True) &
              (db.auth_permission.group_id == db.auth_group.id) &
              (db.sender.id == db.auth_permission.record_id) &
              (db.auth_group.id == db.auth_membership.group_id) &
              (db.auth_user.id == db.auth_membership.user_id) &
              (db.auth_user.id == auth.user_id),
              ignore_common_filters=True).select(db.sender.sender_prefix,
                                                 db.sender.title,
                                                 db.sender.id,
                                                 db.sender.extra)
    senders = []
    ids = []
    sid = {}
    sender_prefix = {}
    for row in rows:
        senders.append(row.title + " - " + row.sender_prefix)
        ids.append(row.id)
        sid[row.id] = row.extra
        sender_prefix[row.id] = row.sender_prefix

    compose_form = SQLFORM.factory(Field('to', type='string', required=True, label=T('Send to'),
                                         comment=T('Prefix with # for groups and @ for users')),
                                   Field('message', type='string', required=True, label=T('Message'), comment=T('')),
                                   Field('sender', type='string', required=True, label=T('Sender'), comment=T(''),
                                         requires=IS_IN_SET(ids, senders))
                                   )
    if compose_form.process().accepted:
        sms = pickle.dumps({'message': compose_form.vars.message,
                            'to': compose_form.vars.to,
                            'sender': sender_prefix[int(compose_form.vars.sender)],
                            'sid': sid[int(compose_form.vars.sender)]})
        queue_manager.send_sms(sms=sms)
        pass
    return dict(form=compose_form)
