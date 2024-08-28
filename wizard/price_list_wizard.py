from odoo import models, fields, api
from odoo.exceptions import UserError


class PricelistWizard(models.TransientModel):
    _name = 'pricelist.wizard'
    _description = 'Pricelist Wizard'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', string='Product')
    pricelist_ids = fields.One2many('pricelist.wizard.line',
                                    'wizard_id',
                                    string='Available Pricelists')
    selected_pricelist_id = fields.Many2one('product.pricelist',
                                            string='Selected Pricelist',
                                            compute='_compute_selected_pricelist')

    @api.onchange('pricelist_ids')
    def _onchange_selected(self):
        selected_line = self.pricelist_ids.filtered('selected')
        if selected_line:
            for line in self.pricelist_ids:
                if line != selected_line:
                    line.selected = False

    @api.depends('pricelist_ids.selected')
    def _compute_selected_pricelist(self):
        for wizard in self:
            selected_line = wizard.pricelist_ids.filtered('selected')
            wizard.selected_pricelist_id = selected_line.pricelist_id if selected_line else False

    @api.model
    def default_get(self, fields_list):  # Renamed from `fields` to `field_names`
        res = super(PricelistWizard, self).default_get(fields_list)
        sale_order_line_id = self.env.context.get('default_sale_order_line_id')
        sale_order_line = self.env['sale.order.line'].browse(sale_order_line_id)
        product_tmpl_id = sale_order_line.product_id.product_tmpl_id.id

        pricelist_lines = []
        pricelists = self.env['product.pricelist'].search([])
        for pricelist in pricelists:
            valid_pricelist_items = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', pricelist.id),
                ('product_tmpl_id', '=', product_tmpl_id),
            ])
            if valid_pricelist_items:
                pricelist_lines.append((0, 0, {
                    'pricelist_id': pricelist.id,
                    'name': pricelist.name,
                    'selected': False,
                }))

        res.update({
            'sale_order_line_id': sale_order_line_id,
            'product_id': sale_order_line.product_id.id,
            'pricelist_ids': pricelist_lines
        })
        return res

    def apply_pricelist(self):
        print("=============================================================")
        print("Selected Pricelist:", self.selected_pricelist_id.name if self.selected_pricelist_id else "None")

        if not self.selected_pricelist_id:
            raise UserError("No pricelist is selected. Please select a pricelist.")

        sale_order_line = self.sale_order_line_id
        sale_order = sale_order_line.order_id

        valid_pricelist_items = self._get_valid_pricelist_items(sale_order_line, self.selected_pricelist_id)

        if valid_pricelist_items:
            self._update_order_line_price(sale_order_line, valid_pricelist_items)
            self._update_sale_order_pricelist(sale_order, self.selected_pricelist_id)
            return {'type': 'ir.actions.act_window_close'}
        else:
            raise UserError("The selected pricelist is not valid for the current conditions.")

    def _get_valid_pricelist_items(self, sale_order_line, pricelist):
        domain = [
            ('pricelist_id', '=', pricelist.id),
            ('date_start', '<=', fields.Date.today()),
            '|',
            ('date_end', '>=', fields.Date.today()),
            ('date_end', '=', False),
            ('min_quantity', '<=', sale_order_line.product_uom_qty)
        ]
        items = self.env['product.pricelist.item'].search(domain)
        return items

    def _update_order_line_price(self, sale_order_line, valid_pricelist_items):
        sale_order_line.write({'price_unit': valid_pricelist_items.fixed_price})

    def _update_sale_order_pricelist(self, sale_order, selected_pricelist):
        sale_order.write({'pricelist_id': selected_pricelist.id})