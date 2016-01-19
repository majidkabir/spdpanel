__author__ = 'majidkabir'

export_classes = dict(csv_with_hidden_cols=False,
                      xml=False,
                      html=False,
                      tsv_with_hidden_cols=False,
                      tsv=False,
                      json=False
                      )


@auth.requires_login()
def manage_groups():
    """
    Return all groups that current user is owner of them
    if current user is admin, return all groups
    """
    if auth.has_membership('admin'):
        query = auth.settings.table_group
    else:
        query = auth.settings.table_group.group_owner == auth.user_id

    grid = SQLFORM.grid(query,
                        links=[lambda row: A(T('members'), _href=URL('group_members', vars=dict(id=row.id))),
                               lambda row: A(T('sender IDs'), _href=URL('group_permissions', vars=dict(id=row.id)))],
                        exportclasses=export_classes
                        )
    return dict(grid=grid)


@auth.requires(auth.has_membership('admin') or request.get_vars.id != None and
               auth.settings.table_group[request.get_vars.id] != None and
               auth.settings.table_group[request.get_vars.id].group_owner == auth.user_id)
def group_members():
    """
    Return a list that contains the member of this group
    groupid send to this function with id in url.
    """
    grid = SQLFORM.grid(db.auth_membership.group_id == request.get_vars.id,
                        exportclasses=export_classes
                        )
    return dict(grid=grid)


@auth.requires(auth.has_membership('admin') or request.get_vars.id != None and
               auth.settings.table_group[request.get_vars.id] != None and
               auth.settings.table_group[request.get_vars.id].group_owner == auth.user_id)
def group_permissions():
    """
    Return list of sender id that binds to this group,
    groupid send to this function with id in url.
    """
    if request.args(0) == 'new':
        redirect(URL('add_senderid_to_group', vars=dict(id=request.get_vars.id)))
    else:
        grid = SQLFORM.grid(
            (db.auth_permission.group_id == request.get_vars.id) & (db.auth_permission.table_name == 'sender'),
            exportclasses=export_classes,
            fields=(db.auth_permission.id,
                    db.auth_permission.record_id,
                    db.auth_permission.group_id
                    ),
            links=[dict(header=T('Sender ID'), body=lambda row: db.sender[row.record_id].sender_prefix)]
        )
    return dict(grid=grid)


@auth.requires_login()
def manage_users():
    grid = SQLFORM.grid(auth.table_user(),
                        exportclasses=export_classes)
    return dict(grid=grid)


@auth.requires_login()
def manage_sender_id():
    if auth.has_membership('admin'):
        editable = True
        deletable = True
        create = True
        query = db.sender
    else:
        editable = False
        deletable = False
        create = False
        query = ((db.auth_permission.group_id == db.auth_group.id) &
                 (db.sender.id == db.auth_permission.record_id) &
                 (db.auth_group.id == db.auth_membership.group_id) &
                 (db.auth_user.id == db.auth_membership.user_id) &
                 (db.auth_user.id == auth.user_id))

    grid = SQLFORM.grid(query,
                        fields=[db.sender.id, db.sender.title, db.sender.sender_prefix, db.sender.extra, db.sender.isactive],
                        ignore_common_filters=True,
                        editable=editable,
                        deletable=deletable,
                        create=create,
                        exportclasses=export_classes
                        )
    return dict(grid=grid)


@auth.requires(auth.has_membership('admin') or request.get_vars.id != None and
               auth.settings.table_group[request.get_vars.id] != None and
               auth.settings.table_group[request.get_vars.id].group_owner == auth.user_id)
def add_senderid_to_group():
    if auth.has_membership('admin'):
        rows = db(db.sender,
                  ignore_common_filters=True).select()
    else:
        rows = db((db.auth_permission.group_id == db.auth_group.id) &
                  (db.sender.id == db.auth_permission.record_id) &
                  (db.auth_group.id == db.auth_membership.group_id) &
                  (db.auth_user.id == db.auth_membership.user_id) &
                  (db.auth_user.id == auth.user_id),
                  ignore_common_filters=True).select(db.sender.sender_prefix,
                                                     db.sender.title,
                                                     db.sender.id)
    senders = []
    ids = []
    for row in rows:
        senders.append(row.title + " - " + row.sender_prefix)
        ids.append(row.id)
    form = SQLFORM.factory(Field('to',
                                 type='string',
                                 required=True,
                                 label=T('Send to'),
                                 requires=IS_IN_SET(ids, senders)))
    if form.process().accepted:
        db.auth_permission.insert(group_id=request.get_vars.id,
                                  name='sender_permission',
                                  table_name='sender',
                                  record_id=request.vars.to)
        redirect(URL('group_permissions', vars=request.vars))
    return dict(form=form)
