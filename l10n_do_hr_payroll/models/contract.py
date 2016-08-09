# -*- coding: utf-8 -*-


from openerp import models, fields, api, exceptions

from datetime import datetime, timedelta


class HrContract(models.Model):
    _name = "hr.contract"
    _inherit = ['mail.thread', "hr.contract"]

    log_ids = fields.One2many("salary.log", "contract_id", string="Historial de salarios")
    state = fields.Selection([("draft","Borrador"),
                               ("active","Activo"),
                               ("req_liquidated",u"Solicitud de Liquidación"),
                               ("liquidated", "Liquidado")], default="draft", string="Estado")

    @api.onchange("trial_date_start")
    def onchange_trial_date_start(self):
        trial_date_start = datetime.strptime(self.trial_date_start, "%Y-%m-%d").date()
        trial_date_end = (trial_date_start+timedelta(3 * 365 / 12))
        date_start = (trial_date_end+timedelta(days=1))
        self.trial_date_end = trial_date_end.isoformat()
        self.date_start = date_start.isoformat()

    @api.multi
    def set_active(self):
        self.state = "active"

    @api.multi
    def set_draft(self):
        self.state = "draft"

    @api.multi
    def set_req_liquidated(self):
        self.state = "req_liquidated"

    @api.multi
    def set_liquidated(self):
        self.state = "liquidated"

    @api.multi
    def write(self, vals):
        if "wage" in vals:
            for rec in self:
                self.env["salary.log"].create({"contract_id": rec.id, "wage": vals["wage"]})
        return super(HrContract, self).write(vals)



class SalaryLog(models.Model):
    _name = "salary.log"
    _order = "create_date"

    contract_id = fields.Many2one("hr.contract", string="Contrato")
    wage = fields.Float(string="Salario")