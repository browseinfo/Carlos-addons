# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Experts Working S.R.L. (<http://www.expertsworking.com>).
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

from openerp.osv import orm,fields, osv
from openerp import api
from BeautifulSoup import BeautifulSoup
import subprocess
import urllib, urllib2
from urllib import urlencode
import openerp.addons.decimal_precision as dp
import re
import datetime
from datetime import date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from httplib2 import Http

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    # Calcular el 13% del monto total
    def _count_amt(self, cr, uid, ids, name, args, context=None):
        result = {}
        for data in self.browse(cr, uid, ids, context):
            result[data.id] = data.amount_total * 0.13 or 0.00
        return result

    # Generar el Codigo de Control
#     def _count_control_code(self, cr, uid, ids, name, args, context=None):
#         result = {}
#         date = False
#         for data in self.browse(cr, uid, ids, context):
#             if data.date_invoice:
#                 date = datetime.datetime.strptime(data.date_invoice, DEFAULT_SERVER_DATE_FORMAT).strftime('%Y%m%d')
#             h = Http()
#             url_data = dict(AUTH_NUMBER=int(data.qr_code_id.auth_number),INVOICE_NUMBER=int(data.invoice_number),NIT_CODE_CUSTOMER=int(data.nit),DATE=int(date),AMOUNT=data.amount_total,KEYGEN=str(data.qr_code_id.keygen or ''))
#             url= urlencode(url_data)
#             print 'Datos para el Codigo de Control:',url
# #            resp = 'cc'
# #            resp = urllib2.urlopen('http://104.156.57.114:10001/cc/codigo_control.php?'+url)
#             resp = urllib2.urlopen('http://localhost/cc/codigo_control.php?'+url)
#             soup = BeautifulSoup(resp)
#             result[data.id] = str(soup) or ''
#         return result

    # Obtener el 1ro de cada mes
    def _get_month_first_date(self, cr, uid, ids, name, args, context=None):
        result = {}
        for data in self.browse(cr, uid, ids):
            today_date = datetime.date.today().strftime('%d')
            if today_date == 1:
                seq = {
                    'name': 'QR Customer Invoice',
                    'implementation':'standard',
                    'code': 'account.invoice',
                    'prefix': '',
                    'padding': 1,
                    'number_increment': 1
                }
                self.pool.get('ir.sequence').create(cr, uid, seq)
            result[data.id] = today_date
        return result

    # Obtener el Total + Comision
    def _get_total_plus_comision(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        total_plus_discount_amount = 0.00
        if ids:
            for self_obj in self.browse(cr, uid, ids):
                
                #venta_origen = self.pool.get('sale.order').search(cr, uid, [('name', 'in', self_obj.origin)], context=context)
                
                ventas = self.pool.get('sale.order')
                venta_origen = ventas.search(cr, uid, [('name','=', self_obj.origin)], context=context)
                
                for line in self_obj.invoice_line:
                    total_plus_discount_amount += line.price_subtotal
                    print '______subtotal______',line.price_subtotal
                res[self_obj.id] = total_plus_discount_amount #+ venta_origen.comision
        print '______total mas descuento______',res
        
        return res

    # Generar el QR
    def _get_qr_code(self, cr, uid, ids, context=None):
        qr_code_ids = self.pool.get('account.invoice').search(cr, uid, [('qr_code_id', 'in', ids)], context=context)
        return qr_code_ids

    # Obtener las lineas de la factura
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    # Valida si la factura no es rectificada, tiene impuestos, si ha sido pagada o Validada.
    def _invoice_number(self, cr, uid, ids, field_name, args, context=None):
        print 'Entrado a la funcion de numeracion'
        res = {}
        tax_flag = 0
        refund_flag = 0
        for self_obj in self.browse(cr, uid, ids):
            for inv_line in self_obj.invoice_line:
      
                if inv_line.invoice_line_tax_id:
                    tax_flag = 1
            
            if (tax_flag == 1) & (self_obj.type != 'out_refund') & ((self_obj.state == 'open') or (self_obj.state == 'paid')) :
                print 'Procesando numero de factura:',self_obj
                invoice_search = self.pool.get('account.invoice').search(cr, uid, 
                                [('qr_code_id.nit_code_comapny','=',self_obj.qr_code_id.nit_code_comapny),
                                ('id','!=',self_obj.id),
                                ('invoice_number','!=',False)
                                ])
                res[self_obj.id] = len(invoice_search) + 1
            else:
                res[self_obj.id] = 0
        return res
        
    
    # Campos adicionales para la Factura
    _columns = {
        'shop_id': fields.many2one('stock.warehouse', 'Tienda'),
        'qr_code_id': fields.many2one('qr.code', 'Dosificacion Tienda'),
        'nit': fields.char('NIT', size=11),
        'legal_customer_name': fields.char('Razon Social', size=32),
        'razon': fields.char('Razón Social',size=124,help="Nombre o Razón Social para la Factura."),
        'amt_thirteen': fields.function(_count_amt, string="Amount*0.13", type='float'),
#         'control_code': fields.function(_count_control_code, string="Codigo Control", readonly=True, states={'draft': [('readonly', False)]}, type='char', size=17, store=
#                                         {
#                                         'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['qr_code_id', 'nit', 'date_invoice', 'invoice_number', 'amount_total'], 10),
#                                         'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#                                         'qr.code': (_get_qr_code, ['auth_number', 'keygen', 'nit_code_comapny'], 10),
#                                     }
#                                         ),
        'get_month_first_date': fields.function(_get_month_first_date, string="Month Date", type="integer"),
        'invoice_number': fields.function(_invoice_number, string='Numero Factura', store=True, type="char"),
        'order_status': fields.selection([('anulada', 'ANULADA'), ('extraviada', 'EXTRAVIADA'), ('valida','VALIDA'),('no_utilizada','NO UTILIZADA'),('emitida_por_contingencia','EMITIDA POR CONTINGENCIA')], 'Estado de Factura'),
        'invoice_authorization_relacion': fields.related('qr_code_id', 'auth_number', type='char', string='Numero Autorizacion', readonly=True),
        'total_plus_comision': fields.function(_get_total_plus_comision, string='Total + Comision', store=True),
    }
    
    _defaults = {
        'date_invoice': date.today().strftime('%Y-%m-%d'),
        'order_status': 'valida',
    }
    
    # Cuando cambia la Tienda en el formulario
    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        domain = {}
        data = self.pool.get('stock.warehouse').browse(cr, uid, shop_id, context=context)
        qr_code_ids = [qr.id for qr in data.qr_code_ids]
        domain = [('id', '=', qr_code_ids)]
        return {'domain': {'qr_code_id': domain}}

    @api.multi
    # Cuando se cambia el cliente
    def onchange_partner_id(self, type, partner_id,\
        date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice,self).onchange_partner_id( type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        if partner_id:
            p = self.env['res.partner'].browse(partner_id)
            result['value']['nit'] = p.commercial_partner_id.nit
            result['value']['legal_customer_name'] = p.legal_name_customer
        return result
    
    # Cancelar la factura pero verificar que no tenga pagos
    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.write({'state': 'cancel', 'order_status': 'anulada', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        self._log_event(-1.0, 'Cancel Invoice')
        return True    
    
    # Cuando se presiona el boton de impresion
    def print_qr_report(self, cr, uid, ids, context):
        for data in self.browse(cr, uid, ids):
            if data.qr_code_id.print_formate == 'original_a':
                datas = {
                    'ids': ids,
                    'model': 'account.invoice',
                    'form': self.read(cr, uid, ids[0], context=context)
                }
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'factura_receipt',
                    'datas': datas,
                    'nodestroy' : True
                }
            if data.qr_code_id.print_formate == 'original_b':
                datas = {
                    'ids': ids,
                    'model': 'account.invoice',
                    'form': self.read(cr, uid, ids[0], context=context)
                }
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'anverso_receipt',
                    'datas': datas,
                    'nodestroy' : True
                }

# Modelo para punto de venta
class sale_shop(orm.Model):
    _inherit = 'stock.warehouse'
    _columns = {
        'qr_code_ids': fields.many2many('qr.code', 'invoice_qr_code_rel', 'invoice_id', 'qr_id', 'Dosificacion Tienda'),
    }
sale_shop()

# Modelo para QR 
class qr_code(orm.Model):
    _name = 'qr.code'
    _rec_name = 'nit_code_comapny'

    _columns = {
        'nit_code_comapny': fields.char('NIT de la Empresa', size=50),
        'company_name': fields.many2one('res.company', 'Empresa'),
        'invoice_number': fields.integer('Numero de Factura', size=10),
        'invoice_authorization': fields.integer('Numero de Autorizacion', size=15),
        'qr_date': fields.date('Fecha'),
        'amount': fields.float('Monto', size=11),
        'date_limit': fields.date('Fecha Limite'),
        'ice': fields.integer('ICE'),
        'ivg': fields.integer('IVG'),
        'nit_code_customer': fields.char('NIT del Cliente', size=12),
        'legal_customer_name': fields.char('Nombre Legal del Cliente', size=255),
        'auth_number': fields.char('Numero de Autorizacion', size=32),
        'keygen': fields.char('Llave de Dosificacion', size=255),
        'code': fields.char('Sucursal', size=32),
        'street1': fields.char('Direccion 1', size=100),
        'street2': fields.char('Direccion 2', size=100),
        'phone': fields.integer('Telefono'),
        'city': fields.char('Ciudad', size=100),
        'description': fields.text('Actividad Economica'),
        'slogan': fields.char('Leyenda', size=255),
        'print_formate': fields.selection([('original_a', 'Ancho'), ('original_b', 'Tira')], string="Formato de Impresion", required=True)
    }
    
qr_code()

# Anula la factura que es resultado de una devolucion
class account_invoice_refund(osv.osv_memory):

    _inherit = "account.invoice.refund"

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        inv_obj = self.pool.get('account.invoice')
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_m_line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        inv_tax_obj = self.pool.get('account.invoice.tax')
        inv_line_obj = self.pool.get('account.invoice.line')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in self.browse(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(cr, uid, uid, context=context).company_id
            journal_id = form.journal_id.id
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                
                # Cambiar el estatus de la factura a ANULADA en la factura original
                inv_obj.write(cr, uid, [inv.id], {'order_status': 'anulada'})
                
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(_('Error!'), _('Cannot %s draft/proforma/cancel invoice.') % (mode))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(_('Error!'), _('Cannot %s invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.') % (mode))
                if form.period.id:
                    period = form.period.id
                else:
                    period = inv.period_id and inv.period_id.id or False

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form.date:
                    date = form.date
                    if not form.period.id:
                            cr.execute("select name from ir_model_fields \
                                            where model = 'account.period' \
                                            and name = 'company_id'")
                            result_query = cr.fetchone()
                            if result_query:
                                cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
                                    and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
                            else:
                                cr.execute("""SELECT id
                                        from account_period where date(%s)
                                        between date_start AND  date_stop  \
                                        limit 1 """, (date,))
                            res = cr.fetchone()
                            if res:
                                period = res[0]
                else:
                    date = inv.date_invoice
                if form.description:
                    description = form.description
                else:
                    description = inv.name

                if not period:
                    raise osv.except_osv(_('Insufficient Data!'), \
                                            _('No period found on the invoice.'))

                refund_id = inv_obj.refund(cr, uid, [inv.id], date, period, description, journal_id, context=context)
                refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                inv_obj.write(cr, uid, [refund.id], {'date_due': date,
                                                'check_total': inv.check_total})
                inv_obj.button_compute(cr, uid, refund_id)

                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconcile_id:
                            line.reconcile_id.unlink()
                    refund.signal_workflow('invoice_open')
                    refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                    for tmpline in  refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(cr, uid, to_reconcile_ids[account],
                                        writeoff_period_id=period,
                                        writeoff_journal_id = inv.journal_id.id,
                                        writeoff_acc_id=inv.account_id.id
                                        )
                    if mode == 'modify':
                        invoice = inv_obj.read(cr, uid, [inv.id],
                                    ['name', 'type', 'number', 'reference',
                                    'comment', 'date_due', 'partner_id',
                                    'partner_insite', 'partner_contact',
                                    'partner_ref', 'payment_term', 'account_id',
                                    'currency_id', 'invoice_line', 'tax_line',
                                    'journal_id', 'period_id','order_status'], context=context)
                        invoice = invoice[0]
                        
                        
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = inv_obj._refund_cleanup_lines(cr, uid, invoice_lines, context=context)
                        tax_lines = inv_tax_obj.browse(cr, uid, invoice['tax_line'], context=context)
                        tax_lines = inv_obj._refund_cleanup_lines(cr, uid, tax_lines, context=context)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description
                        })
                        print '_____invoice____',invoice
                        for field in ('partner_id', 'account_id', 'currency_id',
                                         'payment_term', 'journal_id'):
                                invoice[field] = invoice[field] and invoice[field][0]
                        inv_id = inv_obj.create(cr, uid, invoice, {})
                        if inv.payment_term.id:
                            data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv.payment_term.id, date)
                            if 'value' in data and data['value']:
                                inv_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)

            xml_id = (inv.type == 'out_refund') and 'action_invoice_tree1' or \
                     (inv.type == 'in_refund') and 'action_invoice_tree2' or \
                     (inv.type == 'out_invoice') and 'action_invoice_tree3' or \
                     (inv.type == 'in_invoice') and 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            id = result and result[1] or False

            result = act_obj.read(cr, uid, [id], context=context)[0]
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            
            # Cambiar el estatus de la factura a ANULADA en la factura rectificatoria
            inv_obj.write(cr, uid, created_inv, {'order_status': 'anulada'})
            
            result['domain'] = invoice_domain
            return result

