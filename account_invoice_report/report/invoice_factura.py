# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.report import report_sxw
import datetime
import qrcode
import base64
import amount_to_text_es
import tempfile
from BeautifulSoup import BeautifulSoup
import subprocess
import urllib, urllib2
from urllib import urlencode
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

# Clase para generar la factura formato ANCHO
class invoice_factura(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(invoice_factura,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
            'get_amount': self.get_amount,
            'get_qrcode': self.get_qrcode,
            'get_datelimit': self.get_datelimit,
            'get_username': self.get_username,
            'get_comision':self.getComision,
            'getGranTotal':self.getGranTotal,
            'getTotalComision':self.getTotalComision,
            'getAmountComision':self.getAmountComision,
            'getTaxFlag':self.getTaxFlag,
            'getPriceUnit':self.getPriceUnit,
        })
        
    def getComision(self,so_num):
        saleorder = self.pool.get('sale.order')
        sale_oID = saleorder.search(self.cr, self.uid,[('name','=',so_num)])
        customerPO = saleorder.browse(self.cr, self.uid, sale_oID)
        tipo = saleorder.browse(self.cr, self.uid, sale_oID).comision
        return customerPO
    
    def getTaxFlag(self,tax):
        flag = 0
        if tax:
            flag = 1
        else:
            flag = 0
        return flag
        
    def getGranTotal(self,so_num,subtotal):
        grantotal = self.getComision(so_num).comision + subtotal
        print "Gran total>>>>",grantotal
        return grantotal
    
    def getTotalComision(self, so_num, id_line, subtotal, totalBs):
        comision = 0.00
        #print '>>>>>>>Subtotal ',subtotal
        if self.getTaxFlag(id_line) == 1:
            subtotal = subtotal + (subtotal * 0.13)
            print "con impuesto>>>>>><",subtotal
            
        if self.getComision(so_num).comision != 0.00:
            comision = subtotal + (( subtotal / totalBs) * self.getComision(so_num).comision)
            #print "SUMANDO COMISION ", comision
        else:
            comision = subtotal + (( subtotal / totalBs) * self.getComision(so_num).comision)
            #print "SIN COMISION ", comision
        return comision
    
    def getPriceUnit (self,cantidad,so_num, id_line, subtotal, totalBs):
        print "total antes ", self.getTotalComision(so_num, id_line, subtotal, totalBs)
        print "cantidad ", cantidad
        price_unit = (self.getTotalComision(so_num, id_line, subtotal, totalBs) / cantidad)
        print "price unit ", price_unit
        return price_unit

    def get_username(self):
        user_name = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name
        return user_name

    def get_datelimit(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')

    def get_amount(self, amount, currency):
        amt_en = amount_to_text_es.amount_to_text(amount, 'en', currency)
        return amt_en

    def getAmountComision(self, so_num,subtotal, currency):
        grantotal = self.getComision(so_num).comision + subtotal
        totalLetras = amount_to_text_es.amount_to_text(grantotal, 'en', currency)
        return totalLetras

    def get_qrcode(self, nit_company, auth_no, in_no, ncc, date, amt, keygen, control_code):
#        date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
#        url = 'http://198.178.122.145:8060/cc/codigo_control.php?AUTH_NUMBER=' + str(auth_no or '') + '&INVOICE_NUMBER=' + str(in_no or '') + '&NIT_CODE_CUSTOMER=' + str(ncc or '') + '&DATE=' + str(date or '') + '&AMOUNT=' + str(amt or '') + '&KEYGEN=' + str(keygen or '')
        date = datetime.datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).strftime('%Y%m%d')
        control_code = str(nit_company or '') + '|' + str(in_no or '0') + '|' + str(auth_no or '') + '|' + str(date or '') + '|' + str(amt or '') + '|' + str(control_code or '') + '|' + str(ncc or '') + '|0.00' + '|0.00' + '|0.00' + '|0.00'
#        resp = urllib2.urlopen(url)
#        soup = BeautifulSoup(resp)
        qr_img = qrcode.make(control_code)
        filename = str(tempfile.gettempdir()) + '/qrtest.png'
        qr_img.save(filename)
        return base64.encodestring(file(filename, 'rb').read())

report_sxw.report_sxw('report.factura_receipt','account.invoice','addons/account_invoice_report/report/invoice_factura.rml',parser=invoice_factura)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: