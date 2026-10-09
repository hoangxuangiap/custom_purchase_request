from odoo import models, fields

class PurchaseRequestRejectWizard(models.TransientModel):
    _name = 'purchase.request.reject.wizard'
    _description = 'Lý do từ chối yêu cầu mua hàng'

    reason = fields.Text(string='Lý do từ chối', required=True)

    def action_reject(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            request = self.env['purchase.request'].browse(active_id)
            request.write({
                'state': 'rejected',
                'reject_reason': self.reason
            })
        return {'type': 'ir.actions.act_window_close'}