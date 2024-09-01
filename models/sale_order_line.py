from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def price_list_apply(self):
        self.ensure_one()
        return {
            'name': 'Select Pricelist',
            'type': 'ir.actions.act_window',
            'res_model': 'pricelist.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('order_line_pricelist.pricelist_wizard_form_view').id,
            'target': 'new',
            'context': {'default_sale_order_line_id': self.id},
        }