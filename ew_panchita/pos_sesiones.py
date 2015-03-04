# -*- coding: utf-8 -*-
##############################################################################
#
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

#from openerp import api
from openerp.report import report_sxw
from openerp.osv import fields, osv
from openerp.osv import orm,fields
import time
import datetime
from datetime import timedelta
from openerp.tools.translate import _

class pos_sesion(osv.osv):
    _name = 'pos.sesion'
    ESTADOS_SESION = [
        ('borrador', 'Borrador'),
        ('abierto', 'En Proceso'),
        ('cerrado', 'Cerrado'),
    ]
    _description = 'Modulo de Sesiones'
    _columns = {
		'name': fields.char('Nombre de la Sesion', help='Este es el nombre de la Sesion', required=True),

		'config_id' : fields.many2one('pos.config', 'Punto de Venta', help="Elija el punto de venta de la sesion.", required=True, select=1),
		'pos_session_id' : fields.many2one('pos.session', 'PoS Session'),
		'statement_ids': fields.one2many('account.bank.statement.line', 'pos_statement_id', 'Payments', states={'draft': [('readonly', False)]}, readonly=True),
		'order_ids' : fields.one2many('pos.order', 'session_id', 'Orders'),

		'cajero': fields.many2one('res.users', 'Cajero', required=True, select=1),
		'inicio_caja': fields.float('Cantidad de Apertura Caja', help="Esta es la fecha con la que se inicio la sesion."),#, readonly=True),
		'fecha_apertura': fields.datetime('Fecha Inicio Caja', help="Esta es la fecha con la que se cerro la sesion."),#, readonly=True),
		'fecha_cierre': fields.datetime('Fecha Cierre Caja', help="Selecciona la fecha de cierre de la sesion."),
		'state' : fields.selection(ESTADOS_SESION, 'Estados', required=True, readonly=True, select=1, copy=False),
		'fin_caja' :fields.float('Cantidad de Cierre de Caja', help="Ingrese la cantidad con la que esta cerrando la caja."),
		'total_sesion' : fields.float('Total Sesion', help="Este es el Total de la sesion."),
		'transacciones' : fields.one2many('pos.sesion.transacciones', 'sesiones', 'Transacciones'),
    }
    _defaults = {
    	'name' : fields.date.context_today,
    	'fecha_apertura' : time.strftime("%Y-%m-%d %H:%M:%S"),
        'state' : 'borrador',
        'inicio_caja': 1000,
    }
    
    # Abrir la interface POS
    def open_ui(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)
        context = dict(context or {})
        context['active_id'] = data.pos_session_id.id
        return {
            'type' : 'ir.actions.act_url',
            'url':   '/pos/web/',
            'target': 'self',
        }
    
    # Abrir la Interface de POS.SESION
    def _open_sesion(self, session_id):
        return {
            'name': _('Session'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'pos.sesion',
            'res_id': session_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }    
    
    def apertura_caja(self, cr, uid, ids, context=None):

    	assert len(ids) == 1, "you can open only one session at a time"

    	# Abre el objeto POS.SESSION para crear la sesion del POS
        session = self.pool.get('pos.session')

        # Busca el ID correspondiente en POS.SESION
        wizard = self.browse(cr, uid, ids[0], context=context)
        print "id ", ids[0]
        print "wizard ", wizard
        print "wizard.pos ", wizard.pos_session_id

        # Verifica que exista un registro en POS.SESION relacionado a POS.SESSION
        if not wizard.pos_session_id:
            print "entro del wizard"
            values = {
                'user_id' : uid,
                
                # ID del Punto de Venta
                'config_id' : wizard.config_id.id,
            }
            
            # Crear registro en POS.SESSION y obtener el nuevo ID
            session_id = session.create(cr, uid, values, context=context)
            print "session_id ", session_id
            
            # Navegar en la nueva session
            nueva_session = session.browse(cr, uid, session_id, context=context)
            print "s ", nueva_session
            
            # Si la el campo state esta abierto en POS.SESSION, tambien asignar 'abierto' en POS.SESION
            if nueva_session.state=='opened':
                print "s es true ", nueva_session.state
                print "self ", self.open_ui(cr, uid, ids, context=context)
                
                # Cambiar en POS.SESION el state a abierto y guardar el nuevo ID de POS.SESSION en POS.SESION
                self.write(cr, uid, ids, {'state' : 'abierto', 'pos_session_id' : session_id }, context=context)
                
                # Redireccionar a la interface de POS 
                return self.open_ui(cr, uid, ids, context=context)
            # Redireccionar a la interface de POS.SESION
            return self._open_sesion(wizard.id)
        # Redireccionar a la interface de POS.SESION
        return self._open_sesion(wizard.id)
        return True

    # Cierre de Caja
    def cierre_caja(self, cr, uid, ids, context=None):
        
        # Obtener los valores de POS.SESION
        sesion = self.browse(cr, uid, ids[0], context=context)
        
        # Cambiar el estado a cerrado
        self.write(cr, uid, ids, {'state' : 'cerrado'}, context=context)
        
        # Abre el objeto POS.SESSION para crear la sesion del POS
        session = self.pool.get('pos.session')
        
        # Navegar en la nueva session
        session_pos = session.browse(cr, uid, sesion.pos_session_id , context=context)
        
        # Cambiar el estado a cerrado en POS.SESSION
        # session.write(cr, uid, ids[0], {'state' : 'closed'}, context=context)
        for session_row in session.browse(cr, uid, [sesion.pos_session_id] , context=context):
            
            # session_pos.state = 'closed'
            session.write(cr, uid, session_row[0].id.id, { 'state' : 'closed' })

        return True
        

    def _confirm_orders(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        pos_order_obj = self.pool.get('pos.order')
        for session in self.browse(cr, uid, ids, context=context):
            local_context = dict(context or {}, force_company=session.config_id.journal_id.company_id.id)
            order_ids = [order.id for order in session.order_ids if order.state == 'paid']

            move_id = account_move_obj.create(cr, uid, {'ref' : session.name, 'journal_id' : session.config_id.journal_id.id, }, context=local_context)

            pos_order_obj._create_account_move_line(cr, uid, order_ids, session, move_id, context=local_context)

            for order in session.order_ids:
                if order.state == 'done':
                    continue
                if order.state not in ('paid', 'invoiced'):
                    raise osv.except_osv(
                        _('Error!'),
                        _("You cannot confirm all orders of this session, because they have not the 'paid' status"))
                else:
                    pos_order_obj.signal_workflow(cr, uid, [order.id], 'done')

        return True

    def ajuste_caja(self, cr, uid, ids, context=None):
    	
    	# -----------
    	# ventas_pool = self.pool.get('sale.order')
    	# id_sesion_actual = self.read(cr,uid,ids)[0]['id']
    	# print "id_sesion ", id_sesion_actual
    	# ventas_search = ventas_pool.search(cr, uid, [('sesion', '=', id_sesion_actual)])
    	# print "ventas_search ",ventas_search

    	# for ventas in ventas_pool.browse(cr, uid, ventas_search):
    	# 	print "Venta: ", ventas.name, " Total: ", ventas.amount_total
    	# -----------

    	# -----------
        self.write(cr, uid, ids, {'state' : 'borrador'}, context=context)
        
        # wizard = self.browse(cr, uid, ids[0], context=context)
        # wizard.pos_session_id.signal_workflow('cashbox_control')
        # return self.apertura_caja(cr, uid, ids, context)

        # -----------

        # return {
        #     'type' : 'ir.actions.client',
        #     'name' : 'Point of Sale Menu',
        #     'tag' : 'reload',
        #     'params' : {'menu_id': obj2},
        # }
        return 0

class pos_sesion_transacciones(orm.Model):
	_name = 'pos.sesion.transacciones'
	_columns = {
		'sesiones' : fields.many2one('pos.sesion', 'Sesion'),
		'motivo' : fields.char('Motivo', required=True, help='Escriba el Motivo de la transaccion'),
		'responsable': fields.many2one('res.users', 'Responsable', required=True, select=1),
		'moneda': fields.selection([('bolivianos','Bs.'),('dolares','$us')], 'Moneda'),
		'monto': fields.float('Monto', required=True, help='Ingrese la cantidad de la transaccion'),
		'tipo_transaccion' : fields.many2one('tipo.transaccion', 'Tipo'),
	}
	_defaults = {
		'moneda' : 'bolivianos',
	}

class pos_sesion_transacciones_tipo(orm.Model):
	_name = 'tipo.transaccion'
	_rec_name = 'tipo_transaccion_id'
	_columns = {
		'tipo_transaccion_id' : fields.char('Tipo de Transaccion')
	}

class pos_sesion_pagos(osv.osv):
	_inherit = 'account.voucher'
	_columns = {
		'moneda' : fields.selection([('bolivianos','Bs.'),('dolares','$us')]),
		'dolares' : fields.float('Importe $us', help='Ingrese el monto en dolares'),
		'tasa' : fields.float('Tasa de Cambio', help='Cambio de moneda'),
		'cambio_cliente' : fields.float('Cambio', help='Es el cambio que recibira el cliente por pago de dolares'),
		'sesion_pago' : fields.boolean('NO HAY SESION ABIERTA', required=True),
	}
	_defaults = {
		'moneda' : 'bolivianos',
		'tasa' : 6.96,
	}

	def button_proforma_voucher(self, cr, uid, ids, context=None):
		fecha_actual = time.strftime("%Y-%m-%d %H:%M:%S")
		sesiones_pool = self.pool.get('pos.sesion')
		sesiones_search = sesiones_pool.search(cr,uid,[('fecha_apertura','<', fecha_actual),('state','<>','cerrado')])

		if sesiones_search:
			id_tipo = 0
			voucher_actual = self.read(cr,uid,ids)
			tipo_transaccion_pool = self.pool.get('tipo.transaccion')
			tipo_transaccion_search = tipo_transaccion_pool.search(cr,uid,[])
			transacciones_pool = self.pool.get('pos.sesion.transacciones')

			for tipo in tipo_transaccion_pool.browse(cr,uid,tipo_transaccion_search):
				if tipo.tipo_transaccion_id == "Pago por Ventas":
					id_tipo = tipo.id

			if id_tipo == 0:
				tipo_transaccion_pool.create(cr,uid,{'tipo_transaccion_id':'Pago por Ventas'})
				tipo_transaccion_search = tipo_transaccion_pool.search(cr,uid,[])
				for tipo in tipo_transaccion_pool.browse(cr,uid,tipo_transaccion_search):
					if tipo.tipo_transaccion_id == "Pago por Ventas":
						id_tipo = tipo.id

			for sesiones in sesiones_pool.browse(cr,uid,sesiones_search):
				id_sesion = sesiones.id

			if voucher_actual[0]['moneda'] == 'dolares':
				if voucher_actual[0]['dolares'] > 0 and voucher_actual[0]['tasa'] > 0:
					valores = {
						'motivo':'Ventas Prueba', 
						'responsable':voucher_actual[0]['create_uid'][0], 
						'monto':voucher_actual[0]['amount'], 
						'moneda':voucher_actual[0]['moneda'], 
						'tipo_transaccion':id_tipo,
						'sesiones':id_sesion
					}
					print "dolares add ", valores
					transacciones_pool.create(cr, uid, valores)
					bolivianos_convertidos = voucher_actual[0]['dolares'] * voucher_actual[0]['tasa']
					if voucher_actual[0]['amount'] < bolivianos_convertidos:
						id_tipo = 0
						for tipo in tipo_transaccion_pool.browse(cr,uid,tipo_transaccion_search):
							if tipo.tipo_transaccion_id == "Cambio por Venta a Dolares":
								id_tipo = tipo.id

						if id_tipo == 0:
							tipo_transaccion_pool.create(cr,uid,{'tipo_transaccion_id':'Cambio por Venta a Dolares'})
							tipo_transaccion_search = tipo_transaccion_pool.search(cr,uid,[])
							for tipo in tipo_transaccion_pool.browse(cr,uid,tipo_transaccion_search):
								if tipo.tipo_transaccion_id == "Cambio por Venta a Dolares":
									id_tipo = tipo.id

						cambio = bolivianos_convertidos - voucher_actual[0]['amount']
						valores = {
							'motivo':'Cambio Prueba',
							'responsable':voucher_actual[0]['create_uid'][0], 
							'monto':cambio, 
							'moneda':'bolivianos', 
							'tipo_transaccion':id_tipo,
							'sesiones':id_sesion
						}
						print "cambio add ", valores
						transacciones_pool.create(cr, uid, valores)
				
				else:
					return {
						'type': 'ir.actions.client',
						'tag': 'action_warn',
						'name': _('Dolares'),
						'params': {
							'title': _('Pago en Dolares'),
							'text': _('Por favor los valores mayores a cero!'),
							'sticky': False
						}
					}
			else:
				valores = {
					'motivo':'Ventas Prueba', 
					'responsable':voucher_actual[0]['create_uid'][0], 
					'monto':voucher_actual[0]['amount'], 
					'moneda':voucher_actual[0]['moneda'], 
					'tipo_transaccion':id_tipo,
					'sesiones':id_sesion
				}
				print "bolivianos add ", valores
				transacciones_pool.create(cr, uid, valores)

		else:
			return {
				'type': 'ir.actions.client',
				'tag': 'action_warn',
				'name': _('Sesiones'),
				'params': {
					'title': _('No existe Sesion Abierta'),
					'text': _('Por favor crear una Sesion con fecha vigente!'),
					'sticky': False
				}
			}
		# -------------------------------------- Nativo colocar despues
		# self.signal_workflow(cr, uid, ids, 'proforma_voucher')
		# return {'type': 'ir.actions.act_window_close'}

	def proforma_voucher(self, cr, uid, ids, context=None):
		self.action_move_line_create(cr, uid, ids, context=context)
		return True

	def action_move_line_create(self, cr, uid, ids, context=None):
		'''
		Confirm the vouchers given in ids and create the journal entries for each of them
		'''
		if context is None:
		    context = {}
		move_pool = self.pool.get('account.move')
		move_line_pool = self.pool.get('account.move.line')
		for voucher in self.browse(cr, uid, ids, context=context):
			local_context = dict(context, force_company=voucher.journal_id.company_id.id)
			if voucher.move_id:
				continue
			company_currency = self._get_company_currency(cr, uid, voucher.id, context)
			current_currency = self._get_current_currency(cr, uid, voucher.id, context)
			# we select the context to use accordingly if it's a multicurrency case or not
			context = self._sel_context(cr, uid, voucher.id, context)
			# But for the operations made by _convert_amount, we always need to give the date in the context
			ctx = context.copy()
			ctx.update({'date': voucher.date})
			# Create the account move record.
			move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
			# Get the name of the account_move just created
			name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
			move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
			move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
			line_total = move_line_brw.debit - move_line_brw.credit
			rec_list_ids = []
			if voucher.type == 'sale':
				line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
			elif voucher.type == 'purchase':
				line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
			line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

			# Create the writeoff line if needed
			ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
			if ml_writeoff:
				move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
			self.write(cr, uid, [voucher.id], {
				'move_id': move_id,
				'state': 'posted',
				'number': name,
			})
			if voucher.journal_id.entry_posted:
				move_pool.post(cr, uid, [move_id], context={})
			# We automatically reconcile the account move lines.
			reconcile = False
			for rec_ids in rec_list_ids:
				if len(rec_ids) >= 2:
					reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
		return True

	def cambio_para_cliente(self, cr, uid, ids, monto, dolares, tasa, context):
		res = {}
		bolivianos_convertidos = dolares * tasa
		if monto < bolivianos_convertidos:
			cambio = bolivianos_convertidos - monto
		else:
			cambio = 0
		res ['cambio_cliente'] = cambio
		return {'value' : res}