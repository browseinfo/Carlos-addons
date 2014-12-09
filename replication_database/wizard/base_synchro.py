# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today browseinfo (<http://browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''Implements wizard and RPCProxy methods for synchronising objects
across openerp instances'''

import time
import threading
import logging

import xmlrpclib

from openerp.osv import fields, orm
from openerp import pooler

_logger = logging.getLogger(__name__)


class RPCProxyOne(object):
    '''
    returns specific object xmlrpc instances for the RPCProxy object
    '''
    def __init__(self, server, resource):
        self.server = server
        local_url = 'http://%s:%d/xmlrpc/common' % (server.server_url,
                                                    server.server_port)
        rpc = xmlrpclib.ServerProxy(local_url)
        self.uid = rpc.login(server.server_db, server.login, server.password)
        local_url = 'http://%s:%d/xmlrpc/object' % (server.server_url,
                                                    server.server_port)
        self.rpc = xmlrpclib.ServerProxy(local_url)
        self.resource = resource

    def __getattr__(self, name):
        return lambda cr, uid, *args, **kwargs: self.rpc.execute(
                                        self.server.server_db, self.uid,
                                        self.server.password, self.resource,
                                        name, *args
                                        )


class RPCProxy(object):
    '''
    Creates an instance of remote server credentials suitable for using over
    xmlrpc
    '''
    def __init__(self, server):
        self.server = server

    def get(self, resource):
        '''
        Returns the object model of the remote server.  Analagous to
        self.pool.get('res.partner') for example
        '''
        return RPCProxyOne(self.server, resource)


class base_synchro(orm.TransientModel):
    """Synchronization Wizard"""
    _name = 'base.synchro'
    _description = __doc__

    _columns = {
        'server_url': fields.many2one('base.synchro.server', 'Server URL',
                                      required=True),
        'user_id': fields.many2one('res.users', 'Send Result To'),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }

    start_date = time.strftime('%Y-%m-%d, %Hh %Mm %Ss')
    report = []
    report_create = 0
    report_write = 0

    def input(self, cr, uid, ids, record, context=None):
        """
        Hook function to transform values.  Kept for backwards
        compatibility and no longer used in main module.  Note
        change of argument name record (was value)
        """
        return record

    def _special_case_crm_case_history(self):
        '''
        Returns fields for special case crm_case_history.

        Note this result restricts the fields retrieved.  The default
        behaviour is to read all fields
        To add further special cases, they will need to be
        integrated in to this class as OpenERP inheritance
        does not work well for getattr.

        Alternatively in your module you will need something
        like.
        from openerp.addons.base_synchro.wizard.base_synchro import base_synchro

        base_synchro._special_case_<model name replacing . with _> = your_func
        '''
        return ['email', 'description', 'log_id']


    def synchronize(self, cr, uid, server, object_, context=None):
        '''
        Main controller function for synchronisation
        Establishes server connections, finds ids to sync and then
        either writes or creates them depending on requirement
        @return: True
        '''
        pool1 = RPCProxy(server)
        pool2 = pooler.get_pool(cr.dbname)

        self.meta = {}
        ids = []
        model = object_.model_id.model

        if object_.action in ('d', 'b'):
            ids = pool1.get('base.synchro.obj').get_ids(cr, uid,
                model,
                object_.synchronize_date,
                eval(object_.domain),
                {'action':'d'}
            )

        if object_.action in ('u', 'b'):
            ids += pool2.get('base.synchro.obj').get_ids(cr, uid,
                model,
                object_.synchronize_date,
                eval(object_.domain),
                {'action':'u'}
            )
        ids = [list(id_) for id_ in ids]
        ids.sort()
        for idx, (dt, id, action) in enumerate(ids):
            if action == 'd':
                pool_src = pool1
                pool_dest = pool2
            else:
                pool_src = pool2
                pool_dest = pool1

            record_fields = getattr(base_synchro,
                                    '_special_case_%s'.replace('.', '_')
                                    % model, [])

            record = pool_src.get(model).read(cr, uid, [id], record_fields,
                                              context=context)[0]

            if 'create_date' in record:
                del record['create_date']
            [record.update({key:val[0]}) for key, val in record.iteritems()
                                                    if isinstance(val, tuple)]
            record = self.data_transform(cr, uid, pool_src, pool_dest, model,
                                         record, action, context=context)
            id2 = self.get_id(cr, uid, object_.id, id, action, context=context)
            if not (idx % 50):
                pass
            # Filter fields to not sync
            for record_field in object_.avoid_ids:
                if record_field.name in record:
                    del record[record_field.name]

            if id2:
                pool_dest.get(model).write(cr, uid, [id2], record,
                                           context=context)
                self.report_write += 1
            else:
                record = self.input(cr, uid, ids, record, context=context)
                idnew = pool_dest.get(model).create(cr, uid, record,
                                                    context=context)
                self.pool.get('base.synchro.obj.line').create(
                        cr, uid, {'obj_id': object_.id,
                                  'local_id': (action == 'u') and id or idnew,
                                  'remote_id': (action == 'd') and id or idnew
                                  }, context=context
                                                                      )
                self.report_create += 1
            self.meta = {}
        return True

    def get_id(self, cr, uid, object_id, id, action, context=None):
        '''
        Finds the mapped object_id on the remote server and if found
        returns its value otherwise returns False
        '''
        pool = pooler.get_pool(cr.dbname)
        line_pool = pool.get('base.synchro.obj.line')
        field_src = (action == 'u') and 'local_id' or 'remote_id'
        field_dest = (action == 'd') and 'local_id' or 'remote_id'

        rid = line_pool.search(cr, uid, [('obj_id', '=', object_id),
                                         (field_src, '=', id)], context=context)
        result = False
        if rid:
            result = line_pool.read(cr, uid, rid, [field_dest],
                                    context=context)[0][field_dest]
        return result

    def find_record(self, cr, uid, pool_src, pool_dest,
                           object_, id, context=None):
        '''
        Overridable method to implement custom searching for relations
        if required.  Implements special case for res.company in case of
        one company on each server which may have different names or ids.
        '''
        result = {}
        if object_ == 'res.company':
            src_company_ids = pool_src.get(object_).search(cr, uid, [])
            dest_company_ids = pool_dest.get(object_).search(cr, uid, [])
            if len(src_company_ids) == len(dest_company_ids) == 1:
                return dest_company_ids[0]

        names = pool_src.get(object_).name_get(cr, uid, [id])[0][1]
        if pool_dest.get(object_):
            res = pool_dest.get(object_).name_search(cr, uid, names, [], '=')

            if res:
                result = res[0][0]
            else:
                self.report.append('WARNING: Record "%s" on relation %s '
                                       'not found, set to null.' % (names, object_))
                result = False
        return result

    def relation_transform(self, cr, uid, pool_src, pool_dest,
                           object_, id, action, context=None):
        '''
        IN: object and ID
        @return: ID of the remote object computed:
        If object is synchronised, read the sync database
        Otherwise, use the name_search method to find the corresponding relation
        '''
        if not id:
            return False
        pool = pooler.get_pool(cr.dbname)
        cr.execute('''select o.id
                        from base_synchro_obj o
                        left join ir_model m on (o.model_id =m.id)
                        where m.model=%s and o.active''', (object_,))
        obj = cr.fetchone()
        result = False
        if obj:
            #
            # If the object is synchronised and found, set it
            #
            result = self.get_id(cr, uid, obj[0], id, action, context=context)
        else:
            #
            # If not synchronized, try to find it with name_get/name_search
            #
            result = self.find_record(cr, uid, pool_src, pool_dest,
                           object_, id, context=context)

        return result


    def data_transform(self, cr, uid, pool_src, pool_dest, object_,
                       data, action='u', context=None):
        '''
        Prepares relational and functional fields for synchronisation
        '''
        self.meta.setdefault(pool_src, {})

        if not object_ in self.meta[pool_src]:
            self.meta[pool_src][object_] = pool_src.get(object_).fields_get(cr, uid)

        record_fields = self.meta[pool_src][object_]
        for f in record_fields:
            if f not in data:
                continue
            ftype = record_fields[f]['type']
            if ftype in ('function', 'one2many', 'one2one'):
                del data[f]

            elif ftype == 'many2one':
                if (isinstance(data[f], list)) and data[f]:
                    fdata = data[f][0]
                else:
                    fdata = data[f]
                df = self.relation_transform(cr, uid, pool_src, pool_dest,
                                             record_fields[f]['relation'], fdata,
                                             action, context=context)
                data[f] = df
                if not data[f]:
                    del data[f]

            elif ftype == 'many2many':
                res = map(lambda x: self.relation_transform(
                                            cr, uid, pool_src, pool_dest,
                                            record_fields[f]['relation'], x,
                                            action, context=context), data[f])
                data[f] = [(6, 0, [x for x in res if x])]
        del data['id']
        return data

    def upload_download(self, cr, uid, ids, context=None):
        '''
        Find all objects that are created or modified after
        the synchronize_date
        Synchronize these objects
        '''
        start_date = time.strftime('%Y-%m-%d, %Hh %Mm %Ss')
        syn_obj = self.browse(cr, uid, ids, context=context)[0]
        pool = pooler.get_pool(cr.dbname)
        server = pool.get('base.synchro.server').browse(cr, uid,
                                                        syn_obj.server_url.id,
                                                        context=context)
        for object_ in server.obj_ids:
            dt = time.strftime('%Y-%m-%d %H:%M:%S')
            self.synchronize(cr, uid, server, object_, context=context)
            if object_.action == 'b':
                time.sleep(1)
                dt = time.strftime('%Y-%m-%d %H:%M:%S')
            self.pool.get('base.synchro.obj').write(cr, uid, [object_.id],
                                                    {'synchronize_date': dt},
                                                    context=context)
        end_date = time.strftime('%Y-%m-%d, %Hh %Mm %Ss')
        if syn_obj.user_id:
            request = pooler.get_pool(cr.dbname).get('res.request')
            if not self.report:
                self.report.append('No exception.')
            summary = '''Here is the synchronization report:

Synchronization started: %s
Synchronization finnished: %s

Synchronized records: %d
Records updated: %d
Records created: %d

Exceptions:
            ''' % (start_date, end_date, self.report_write + self.report_create,
                   self.report_write, self.report_create)
            summary += '\n'.join(self.report)
            print "\n\n*******request",request
            if request:
                request.create(cr, uid, {
                    'name' : "Synchronization report",
                    'act_from' : uid,
                    'act_to' : syn_obj.user_id.id,
                    'body': summary,
                }, context=context)
            return True

    def upload_download_multi_thread(self, cr, uid, data, context=None):
        '''
        Called from button in wizard.  Creates a seperate thread to run
        synchronisation and then returns to user.
        @note: If we are using threading do we need to get a new database
            cursor in synchronise? Otherwise how do we guarantee it is not
            closed.
        '''
        threaded_synchronization = threading.Thread(target=self.upload_download,
                                                    args=(cr, uid, data, context))
        threaded_synchronization.run()
        data_obj = self.pool.get('ir.model.data')
        id2 = data_obj._get_id(cr, uid, 'base_synchro', 'view_base_synchro_finish')
        if id2:
            id2 = data_obj.browse(cr, uid, id2, context=context).res_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'base.synchro',
            'views': [(id2, 'form')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
