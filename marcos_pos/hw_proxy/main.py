# -*- coding: utf-8 -*-
import logging
import time

_logger = logging.getLogger(__name__)

from openerp import http
from openerp.addons.hw_proxy.controllers.main import Proxy

# drivers modules must add to drivers an object with a get_status() method 
# so that 'status' can return the status of all active drivers
drivers = {}

from threading import Thread, Lock
from Queue import Queue, Empty
from openerp.http import request
import requests
import json
from openerp import exceptions
from pprint import pprint as pp


class IPFDriver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.lock  = Lock()
        self.status = {'status':'connecting', 'messages':[]}
        self.ipf_host = False
        self.nif = False
        self.pos_reference = False
        self.user_id = False
        self.ipf_odoo = False
        self.ipf_ip = False
        self.env = False

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def connected_usb_devices(self):

        # for device in self.supported_devices():
        #     if usb.core.find(idVendor=device['vendor'], idProduct=device['product']) != None:
        #         connected.append(device)
        return {}

    def set_status(self, status, message = None):
        _logger.info(status+' : '+ (message or 'no message'))
        if status == self.status['status']:
            if message != None and (len(self.status['messages']) == 0 or message != self.status['messages'][-1]):
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

        if status == 'error' and message:
            _logger.error('ESC/POS Error: '+message)
        elif status == 'disconnected' and message:
            _logger.warning('ESC/POS Device Disconnected: '+message)

    def get_escpos_printer(self):

        try:
            printer = requests.get(self.ipf_host+"/state", headers={"Content-Type": "application/json"})

            status_code = printer.status_code

            if status_code == 200:
                resp = printer.json()
                if resp["response"]["printer_status"].get("state", False) == "online":
                    self.set_status('connected', 'Connected to impresora fiscal epson')
                    return resp
                else:
                    self.set_status('disconnected', 'La interface no se puede comunicar con la impresora.')
                    return resp
            elif status_code == 404:
                self.set_status('disconnected', 'Fallo la conexion con el print-server de la impresora 404')
                return None
            else:
                self.set_status('disconnected', 'Fallo la conexion con el print-server de la impresora 404')
                return None
        except Exception:
            self.set_status('disconnected', 'Fallo la conexion con el print-server de la impresora NO HOST')
            return None
        except requests.exceptions.ConnectionError:
            raise Exception
            self.set_status('disconnected', 'Fallo la conexion con el print-server de la impresora NO HOST')
            return None

    def get_status(self):
        self.push_task('status')
        return self.status

    def print_ipf(self):
        self.push_task('ipf_print')
        return self.nif

    def send_ipf(self):
        pass

    def run(self):

        if not self.ipf_host:
            _logger.error('ESC/POS cannot initialize, please verify system dependencies.')
            return
        while True:
            try:

                error = True
                timestamp, task, data = self.queue.get(True)
                printer = self.get_escpos_printer()

                if printer == None:
                    if task != 'status':
                        self.queue.put((timestamp,task,data))
                    error = False
                    time.sleep(5)
                    continue
                # elif task == 'receipt':
                #     if timestamp >= time.time() - 1 * 60 * 60:
                #         self.print_receipt_body(printer,data)
                #         printer.cut()
                elif task == 'ipf_print':
                    if timestamp >= time.time() - 1 * 60 * 60:
                       self.send_ipf()
                # elif task == 'cashbox':
                #     if timestamp >= time.time() - 12:
                #         self.open_cashbox(printer)
                elif task == 'printstatus':
                    # self.print_status(printer)
                    pass
                elif task == 'status':
                    pass

                error = False

            except Exception as e:
                self.stop_request = True
            # except HandleDeviceError as e:
            #     print "Impossible to handle the device due to previous error %s" % str(e)
            # except TicketNotPrinted as e:
            #     print "The ticket does not seems to have been fully printed %s" % str(e)
            # except NoStatusError as e:
            #     print "Impossible to get the status of the printer %s" % str(e)
            # except Exception as e:
            #     self.set_status('error', str(e))
            #     errmsg = str(e) + '\n' + '-'*60+'\n' + traceback.format_exc() + '-'*60 + '\n'
            #     _logger.error(errmsg);
            finally:
                if error:
                    self.queue.put((timestamp, task, data))
            #     if printer:
            #         printer.close()

    def push_task(self, task, data = None):
        self.lockedstart()
        self.queue.put((time.time(), task ,data))



ipfdriver = IPFDriver()

class Proxy(Proxy):

    def get_status(self):
        statuses = {}
        for driver in drivers:
            statuses[driver] = drivers[driver].get_status()
        return statuses

    @http.route('/hw_proxy/status_json', type='json', auth='none', cors='*')
    def status_json(self, ipf_odoo=False, ipf_ip=False):
        if ipf_odoo and ipf_ip:
            return self.get_ipf_status(ipf_ip)
        return self.get_status()

    def get_ipf_status(self, ipf_ip):
        ipfdriver.ipf_host = ipf_ip
        status = ipfdriver.get_status()
        # _logger(status)
        return status

    @http.route('/hw_proxy/print_ipf_receipt', type='json', auth='user', cors='*')
    def print_ipf_receipt(self, receipt, ipf_odoo=False, ipf_ip=False, ipf_host=False):
        uid = receipt.get("uid", False)
        if uid and ipf_odoo and ipf_ip:
            time.sleep(2)
            ipf_obj = request.env["ipf.printer.config"]
            invoice_exists = False

            while not invoice_exists:
                request.env.cr.execute("SELECT invoice_id FROM pos_order WHERE pos_reference ILIKE %s", ("%{}%".format(uid),))
                invoice_exists = request.env.cr.fetchone()
                request.env.cr.commit()

            if invoice_exists:
                ipf_dict = request.env["ipf.printer.config"].with_context(active_model="account.invoice", active_id=invoice_exists[0], ipf_host=ipf_host).ipf_print()
                if ipf_dict:
                    try:
                        resp = requests.post("{}{}".format(ipf_ip, "/invoice"), data=json.dumps(ipf_dict))
                        if resp.json().get("status", False) == "success":
                            response = resp.json().get("response", False)
                            id = ipf_dict.get("invoice_id")
                            nif = response.get("nif", "")
                            return request.env["account.invoice"].browse(id).write({"nif": nif})
                        else:
                            return False
                    except Exception:
                        return ipfdriver.set_status('disconnected', 'Fallo la conexion con el print-server de la impresora NO HOST')


