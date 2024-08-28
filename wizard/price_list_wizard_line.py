from odoo import models, fields, api


class PricelistWizardLine(models.TransientModel):
    _name = 'pricelist.wizard.line'
    _description = 'Pricelist Wizard Line'

    wizard_id = fields.Many2one('pricelist.wizard', string='Wizard', ondelete='cascade')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    name = fields.Char(related='pricelist_id.name', string='Name', readonly=True)
    selected = fields.Boolean(string='Selected')
