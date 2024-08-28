from odoo import models, fields, api
from odoo.exceptions import UserError


class PricelistWizard(models.TransientModel):
    _name = 'pricelist.wizard'
    _description = 'Pricelist Wizard'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', required=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', string='Product')
    pricelist_ids = fields.One2many('pricelist.wizard.line', 'wizard_id', string='Available Pricelists')

    @api.model
    def default_get(self, field_names):  # Renamed from `fields` to `field_names`
        res = super(PricelistWizard, self).default_get(field_names)
        sale_order_line_id = self.env.context.get('default_sale_order_line_id')
        sale_order_line = self.env['sale.order.line'].browse(sale_order_line_id)
        product_tmpl_id = sale_order_line.product_id.product_tmpl_id.id

        # Fetch pricelists that contain the specific product
        pricelist_lines = []
        pricelists = self.env['product.pricelist'].search([
            ('product_tmpl_id', '=', product_tmpl_id),
        ])
        if pricelists:
            for pricelist in pricelists:
                pricelist_lines.append((0, 0, {
                    'pricelist_id': pricelist.id,
                    'name': pricelist.name,
                }))

        res.update({
            'sale_order_line_id': sale_order_line_id,
            'product_id': sale_order_line.product_id.id,
            'pricelist_ids': pricelist_lines
        })
        return res

    def apply_pricelist(self):
        selected_pricelist_line = self.pricelist_ids.filtered(lambda x: x.selected)
        if not selected_pricelist_line:
            raise UserError("Please select a pricelist.")

        sale_order_line = self.sale_order_line_id
        sale_order = sale_order_line.order_id

        selected_pricelist = selected_pricelist_line.pricelist_id

        valid_pricelist_items = self._get_valid_pricelist_items(sale_order_line, selected_pricelist)

        if valid_pricelist_items:
            self._update_order_line_price(sale_order_line, valid_pricelist_items)
            self._update_sale_order_pricelist(sale_order, selected_pricelist)
            return {'type': 'ir.actions.act_window_close'}
        else:
            raise UserError("The selected pricelist is not valid for the current conditions.")

    def _get_valid_pricelist_items(self, sale_order_line, pricelist):
        # Adjusted search domain for pricelist items
        return self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist.id),
            ('product_tmpl_id', '=', sale_order_line.product_id.product_tmpl_id.id),
            '|',
            ('date_start', '=', False),  # Allow for items with no start date
            ('date_start', '<=', fields.Date.today()),
            '|',
            ('date_end', '=', False),  # Allow for items with no end date
            ('date_end', '>=', fields.Date.today()),
            ('min_quantity', '<=', sale_order_line.product_uom_qty),
        ])

    def _update_order_line_price(self, sale_order_line, valid_pricelist_items):
        sale_order_line.write({'price_unit': valid_pricelist_items.fixed_price})

    def _update_sale_order_pricelist(self, sale_order, selected_pricelist):
        sale_order.write({'pricelist_id': selected_pricelist.id})

        @api.depends('pricelist_ids.selected')
        def _compute_selected_pricelist(self):
            for wizard in self:
                if any(pl.selected for pl in self.pricelist_ids):
                    selected_line = wizard.pricelist_ids.filtered('selected')
                    wizard.selected_pricelist_id = selected_line.pricelist_id if selected_line else False

    @api.onchange('selected')
    def _onchange_selected(self):
        # print("=================================================")
        # print(list(self))
        if any(self.selected):
            self.selected = False
            # # Unselect all other records
            # for line in self.wizard_id.pricelist_ids:
            #     if line != self:
            #         line.selected = False



