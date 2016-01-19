# coding: utf8
__author__ = 'majidkabir'

db.define_table('sender',
                Field('title','string'),
                Field('sender_prefix','string'),
                Field('extra', 'string'),
                Field('isactive', 'boolean')
                )
