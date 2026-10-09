from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Yêu cầu mua hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Yêu cầu tham chiếu', required=True, copy=False, readonly=True, default=lambda self: 'New')
    request_id = fields.Many2one('res.users', string='Được yêu cầu bởi', default=lambda self: self.env.user, required=True, tracking=True)
    approver_id = fields.Many2one('res.users', string='Người phê duyệt', tracking=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban', tracking=True)
    
    origin = fields.Char(string='Tài liệu nguồn')
    description = fields.Text(string='Mô tả')
    
    date = fields.Date(string='Ngày tạo', default=fields.Date.today, required=True)
    date_approve = fields.Date(string='Ngày phê duyệt', readonly=True)
    reject_reason = fields.Text(string='Lý do từ chối', readonly=True)
    
    request_line_ids = fields.One2many('purchase.request.line', 'request_id', string='Chi tiết yêu cầu', copy=True)
    
    state = fields.Selection([
        ('draft', 'Dự thảo'),
        ('wait', 'Chờ duyệt'),
        ('approved', 'Được phê duyệt'),
        ('rejected', 'Đã từ chối'),
        ('done', 'Hoàn thành')
    ], string='Trạng thái', default='draft', tracking=True, required=True)

    total_qty = fields.Float(string='Tổng số lượng', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='Tổng tiền', compute='_compute_totals', store=True)

    @api.depends('request_line_ids.qty', 'request_line_ids.total')
    def _compute_totals(self):
        for rec in self:
            rec.total_qty = sum(line.qty for line in rec.request_line_ids)
            rec.total_amount = sum(line.total for line in rec.request_line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.sequence') or 'New'
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Bạn không được phép xóa ở trạng thái khác dự thảo")
        return super().unlink()

    def action_submit(self):
        for rec in self:
            if not rec.request_line_ids:
                raise UserError("Vui lòng thêm ít nhất một sản phẩm trước khi gửi yêu cầu!")
            rec.write({'state': 'wait'})

    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approved',
                'date_approve': fields.Date.today()
            })

    def action_reset_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def action_reject_wizard(self):
        self.ensure_one()
        return {
            'name': 'Nhập lý do từ chối',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.onchange('request_id')
    def _onchange_request_id(self):
        if self.request_id and self.request_id.employee_ids:
            self.department_id = self.request_id.employee_ids[0].department_id

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id and self.department_id.manager_id:
            self.approver_id = self.department_id.manager_id.user_id