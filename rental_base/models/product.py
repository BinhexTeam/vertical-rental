# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental = fields.Boolean("Can be Rent")


class ProductProduct(models.Model):
    _inherit = "product.product"

    rental = fields.Boolean("Can be Rent", related="product_tmpl_id.rental", store=True)
