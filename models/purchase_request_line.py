from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Chi tiết yêu cầu mua hàng'

    request_id = fields.Many2one('purchase.request', string='Yêu cầu mua hàng', required=True, ondelete='cascade')
    sequence = fields.Integer(string='STT', default=10)
    product_id = fields.Many2one('product.product', string='Sản phẩm', required=True)
    name = fields.Text(string='Mô tả')
    qty = fields.Float(string='Số lượng', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Đơn vị tính', required=True)
    price_unit = fields.Float(string='Đơn giá')
    qty_approve = fields.Float(string='Số lượng phê duyệt')
    total = fields.Float(string='Thành tiền', compute='_compute_total', store=True)

    @api.depends('qty', 'price_unit')
    def _compute_total(self):
        for line in self:
            line.total = line.qty * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.uom_id = self.product_id.uom_id
            self.price_unit = self.product_id.list_price
            if self.product_id.seller_ids:
                self.price_unit = self.product_id.seller_ids[0].price

    def unlink(self):
        for line in self:
            if line.request_id and line.request_id.state != 'draft':
                raise UserError("Không được phép xóa chi tiết khi không ở trạng thái dự thảo!")
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('request_id'):
                request = self.env['purchase.request'].browse(vals.get('request_id'))
                if request.exists() and request.state != 'draft':
                    raise UserError("Chỉ được phép thêm chi tiết yêu cầu khi ở trạng thái dự thảo!")
        return super().create(vals_list)