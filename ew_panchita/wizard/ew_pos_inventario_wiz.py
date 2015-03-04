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

from openerp.osv import fields, osv
import time
import operator
import itertools
from datetime import datetime
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from openerp.tools.translate import _
from cStringIO import StringIO
import base64
from openerp import netsvc
from openerp import tools


# Declaracion del Wizard
class ew_pos_inventario_wiz_qweb(osv.osv):
    _name="ew.pos_report_inventario.wiz.qweb"
    _columns={
                'start_date': fields.datetime('Desde la Fecha'),
                'end_date': fields.datetime('Hasta la Fecha'),
                'session_id' : fields.many2one('pos.session', 'Turno', required=False),
    }
    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        'end_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    # Accion del Boton de OK en el Wizard
    def printInventoryPdf(self,cr,uid,filtros,context=None):
        data={}
        data['ids'] = filtros
        data['form'] = self.read(cr, uid, filtros, ['start_date','end_date'])[0]
        data['form']['context'] = context
        print '----- Informacion del formulario:',data
        resultadoInventarioWizard = self.pool['report'].get_action(cr, uid, [], 'ew_panchita.pos_inventario', data=data, context=context)
        print '----- Informacion enviada al reporte:',resultadoInventarioWizard

        return resultadoInventarioWizard



    # Accion del Boton de exportacion a Excel
    def inventoryMovement(self,cr,uid,filtros,context=None):
        self.yesterday_stock = 0.00
        self.yesterday_stock_money = 0.00
        self.today_in_stock = 0.00
        self.today_out_stock = 0.00
        self.today_stock = 0.00
        self.today_in_stock_money = 0.00
        self.today_out_stock_money = 0.00
        self.today_stock_money = 0.00
        print "------Filtros:",filtros
        if filtros:
            self_browse = self.browse(cr, uid, filtros[0])
            product_obj = self.pool.get('product.product')
            stock_move_pool = self.pool.get('stock.move')
            result = []
            product_ids = self.pool.get('product.product').search(cr, uid, [('qty_available','>',0)])
            
            
            if product_ids:
                for product in product_obj.browse(cr, uid, product_ids, context=context):
                    
                    #Logic For get yesterday stock (Yesterday Stock (all history before  Initial date)
                    yesterday_stock_search = stock_move_pool.search(cr, uid, [('product_id','=',product.id),
                                                                              ('create_date','<=', self_browse.start_date),
                                                                              ('picking_type_id.code','in',['incoming', 'outgoing']),
                                                                              ('state','not in',['draft','cancel'])])
                    yesterday_stock = 0.00
                    yesterday_stock_money = 0.00
                    if yesterday_stock_search:
                        stock_plus = 0.00
                        stock_minus = 0.00
                        for yesterday_stock in yesterday_stock_search:
                            yesterday_stock_browse = stock_move_pool.browse(cr, uid, yesterday_stock)
                            if yesterday_stock_browse.picking_type_id.code == 'incoming':
                                stock_plus += yesterday_stock_browse.product_uom_qty
                            if yesterday_stock_browse.picking_type_id.code == 'outgoing':
                                stock_minus += yesterday_stock_browse.product_uom_qty
                            yesterday_stock = (stock_plus - stock_minus)
                            yesterday_stock_money = (stock_plus - stock_minus) * yesterday_stock_browse.product_id.standard_price
                    
                    #Logic For get today in stock (Yesterday Stock (In's (between Initial Date)
                    today_stock_search_in = stock_move_pool.search(cr, uid, [('product_id','=',product.id),
                                                                             ('create_date','>=', self_browse.start_date),
                                                                             ('create_date','<=', self_browse.end_date),
                                                                             ('picking_type_id.code','=','incoming'),
                                                                             ('state','not in',['draft','cancel'])])
                    
                    
                    today_in_stock = 0.00
                    today_in_stock_money = 0.00
                    if today_stock_search_in:
                        for today_stock_in in today_stock_search_in:
                            today_stock_in_browse = stock_move_pool.browse(cr, uid, today_stock_in)
                            today_in_stock += today_stock_in_browse.product_uom_qty
                            today_in_stock_money += today_stock_in_browse.product_uom_qty * today_stock_in_browse.product.standard_price
                        self.today_in_stock = today_in_stock
                        self.today_in_stock_money = today_in_stock_money
                        
                        
                    
                    
                    #Logic For get today out stock (Yesterday Stock (Out's (between Final Date))
                    
                    today_stock_search_out = stock_move_pool.search(cr, uid, [('product_id','=',product.id),
                                                                             ('create_date','>=', self_browse.start_date),
                                                                             ('create_date','<=', self_browse.end_date),
                                                                             ('picking_type_id.code','=','outgoing'),
                                                                             ('state','not in',['draft','cancel'])])
                    
                    today_out_stock = 0.00
                    today_out_stock_money = 0.00
                    if today_stock_search_out:
                        for today_stock_out in today_stock_search_out:
                            today_stock_out_browse = stock_move_pool.browse(cr, uid, today_stock_out)
                            today_out_stock += today_stock_out_browse.product_uom_qty
                            today_out_stock_money += today_stock_out_browse.product_uom_qty * today_stock_out_browse.product_id.standard_price
                        self.today_out_stock = today_out_stock
                        self.today_out_stock_money = today_out_stock_money
                        
                    # creando matriz de resultado   
                    dic = {
                           'name': product.name,
                           'yesterday_stock': yesterday_stock,
                           'yesterday_stock_money': yesterday_stock_money,
                           'today_in_stock': today_in_stock,
                           'today_in_stock_money': today_in_stock_money,
                           'today_out_stock': today_out_stock,
                           'today_out_stock_money': today_out_stock_money,
                           'today_stock': product.qty_available,
                           'today_stock_money': product.qty_available * product.standard_price,
                           }
                    self.yesterday_stock += yesterday_stock
                    self.yesterday_stock_money += yesterday_stock_money
                
                    self.today_stock += product.qty_available
                    self.today_stock_money += product.qty_available * product.standard_price
                    
                    result.append(dic)
                    
                    self.resultado = result
                    print "----Resultado de busqueda de inventarios:",result
                    
                    
                # Create an new Excel file and add a worksheet.
                import base64
                filename = 'inventory_movement_report.xls'
                workbook = xlwt.Workbook()
                style = xlwt.XFStyle()
                tall_style = xlwt.easyxf('font:height 720;') # 36pt
                # Create a font to use with the style
                font = xlwt.Font()
                font.name = 'Times New Roman'
                font.bold = True
                font.height = 250
                style.font = font
                worksheet = workbook.add_sheet('Sheet 1')
                first_row = worksheet.row(1)
                first_row.set_style(tall_style)
                first_col = worksheet.col(1)
                first_col.width = 156 * 30
                second_row = worksheet.row(0)
                second_row.set_style(tall_style)
                second_col = worksheet.col(0)
                second_col.width = 236 * 30
                
                worksheet.write(0,0, 'Stock Por Productos', style)
                
                worksheet.write(0,3, 'Fecha Inicial', style)
                worksheet.write(0,4, self_browse.start_date)
                
                worksheet.write(0,5, 'Fecha Final', style)
                worksheet.write(0,6, self_browse.end_date)
                
                worksheet.write(2,0, 'Producto', style)
                worksheet.write(2,1, 'Stock Anterior', style)
                worksheet.write(2,2, 'Ingresos', style)
                worksheet.write(2,3, 'Salidas', style)
                worksheet.write(2,4, 'Stock Actual', style)
                worksheet.write(2,5, 'Stock Anterior Value', style)
                worksheet.write(2,6, 'Ingresos Value', style)
                worksheet.write(2,7, 'Salidas Value', style)
                worksheet.write(2,8, 'Stock Actual Value', style)
                
                row_2 = 3
                for val in result:
                    worksheet.write(row_2, 0, tools.ustr(val['name']))
                    worksheet.write(row_2, 1, val['yesterday_stock'])
                    worksheet.write(row_2, 2, val['today_in_stock'])
                    worksheet.write(row_2, 3, val['today_out_stock'])
                    worksheet.write(row_2, 4, val['today_stock'])
                    worksheet.write(row_2, 5, val['yesterday_stock_money'])
                    worksheet.write(row_2, 6, val['today_in_stock_money'])
                    worksheet.write(row_2, 7, val['today_out_stock_money'])
                    worksheet.write(row_2, 8, val['today_stock_money'])
                    row_2+=1
                
                worksheet.write(row_2 ,0, 'Totales', style)
                worksheet.write(row_2 ,1, self.yesterday_stock, style)
                worksheet.write(row_2 ,2, self.today_in_stock, style)
                worksheet.write(row_2 ,3, self.today_out_stock, style)
                worksheet.write(row_2 ,4, self.today_stock, style)
                worksheet.write(row_2 ,5, self.yesterday_stock_money, style)
                worksheet.write(row_2 ,6, self.today_in_stock_money, style)
                worksheet.write(row_2 ,7, self.today_out_stock_money, style)
                worksheet.write(row_2 ,8, self.today_stock_money, style)
                
                fp = StringIO()
                workbook.save(fp)
                export_id = self.pool.get('excel.extended').create(cr, uid, {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename}, context=context)
                fp.close()
                
                # Redireccionar a el reporte resultado
                return {
                    'view_mode': 'form',
                    'res_id': export_id,
                    'res_model': 'excel.extended',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'target': 'new',
                }
        return True


class inventory_excel_extended(osv.osv_memory):
    _name= "excel.extended"
    _columns= {
               'excel_file': fields.binary('Descargar Reporte Excel'),
               'file_name': fields.char('Excel File', size=64),
               }


    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: