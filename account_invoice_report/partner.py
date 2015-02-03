#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2014 Experts Working S.R.L. (<http://www.expertsworking.com>).
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm

# Heredar el modelo de clientes y agregarle los campos adicionales
class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    _columns = {
        'tipo_cliente_id': fields.many2one('tipo.cliente', 'Tipo Cliente'),
        'nit': fields.char('CI/NIT', size=11, help=u"Número de Identificación Tributaria (o CI para facturación)."),
        #'ci_dept': fields.selection([('lpz','LPZ'),('scz','SCZ'),('ben','BEN'),('cba','CBA'),('chu','CHU'),('oru','ORU'),('pan','PAN'),('pot','POT'),('tja','TJA')],'Dept. CI', help="Lugar de emision Carnet de Identidad"),
        'legal_name_customer': fields.char('Razon Social', size=32),
        #'razon': fields.char(u'Razón Social',size=64,help=u"Razón Social del Cliente."),
        #'razon_invoice': fields.char(u'Razón Social para facturación',size=64,help=u"Razón Social para Facturación."),
        #'ci': fields.char('CI', size=7, help="Carnet de Identidad.")
    }

    # Verificar si el NIT es unico
    def _check_unique_val(self, cr, uid, ids, context=None):

        ir_conf_pool=self.pool.get('ir.config_parameter')
        validate_unique_nit=ir_conf_pool.get_param(cr, uid, 'validate_unique_nit', False, context=context)
        if not validate_unique_nit:
            return True

        fields_check = [('nit','NIT')]
        for partner in self.read(cr, uid, ids, ['nit', 'id'], context=context):
            for field in fields_check:
                field_name = field[0]
                field_desc = field[1]

                val = partner[field_name]
                if val:
                    iden_id = self.search(cr, uid, [(field_name,'=',val),('id','!=',partner['id'])], context=context)
                    if iden_id:
                        iden_name = self.read(cr, uid, iden_id, ['name', 'ref'], context=context)[0]['name']
                        raise osv.except_osv(u'%s inválido' % field_desc, u'Ya existe un socio con el mismo %s. Puede buscarlo como: \n "%s"' % (field_desc,iden_name))
                        return False
        return True
    _constraints = [
        (_check_unique_val, 'Invalido. Los campos NIT y CI deben ser únicos', ['nit','ci']),
    ]
    
    # Cuando cambia el nombre del cliente
    def onchange_name(self, cr, uid, ids, name, context=None):
        return {'value': {'razon': name,
                          'razon_invoice': name}}
    
    # Cuando czambia la razon social
    def onchange_razon(self, cr, uid, ids, razon, context=None):
        return {'value': {'razon_invoice': razon}}

    # Busqueda por nombre
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = set()
            ids.update(self.search(cr, user, args + [('name',operator,name)], limit=limit, context=context))
            if not limit or len(ids) < limit:
                ids.update(self.search(cr, user, args + [('nit',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                #if not limit or len(ids) < limit:
                #    ids.update(self.search(cr, user, args + [('ci',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
            ids = list(ids)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

res_partner()

# Modelo para Tipo de Cliente
class tipo_cliente(orm.Model):
    _name = "tipo.cliente"
    _description = "Tipo de Cliente"
    _rec_name="tipo_cliente"
    _columns = {
        'tipo_cliente': fields.char('Tipo Cliente', size=255, translate=True, required=True, help="Tipo de cliente"),
    }
    _order = "tipo_cliente"

tipo_cliente()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

