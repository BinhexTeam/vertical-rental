# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_rental_interval_price = fields.Boolean(
        string="Show Option Interval Price",
    )
    rental_interval_name = fields.Char(
        string="Rental Interval",
    )

    def _get_number_of_time_unit(self):
        res = super()._get_number_of_time_unit()
        time_uoms = self._get_time_uom()
        if self.product_uom.id == time_uoms["interval"].id:
            res = (self.end_date - self.start_date).days + 1
        return res

    @api.model
    def _get_time_uom(self):
        res = super()._get_time_uom()
        uom_interval = self.env.ref("rental_pricelist_interval.product_uom_interval")
        res["interval"] = uom_interval
        return res

    # (override) _set_product_id from module rental_pricelist
    def _set_product_id(self):
        self.ensure_one()
        time_uoms = self._get_time_uom()
        if (
            self.rental
            and self.order_id.pricelist_id.is_interval_pricelist
            and self.display_product_id.rental_of_interval
        ):
            self.product_uom = time_uoms["interval"]
            self.product_id = self.display_product_id.product_rental_interval_id
        super()._set_product_id()

    def _check_interval_price(self):
        self.ensure_one()
        uom_interval = self.env.ref("rental_pricelist_interval.product_uom_interval")
        if self.product_uom.id == uom_interval.id:
            product = self.product_id.rented_product_id
            if product and product.rental_of_interval:
                uom_qty = self.number_of_time_unit
                if uom_qty > product.rental_interval_max:
                    raise UserError(
                        _(
                            "Max rental interval (%(rental_interval_max)s days) is exceeded."
                        )
                        % {"rental_interval_max": product.rental_interval_max}
                    )

    def _update_interval_price(self):
        self.ensure_one()
        if self.order_id.pricelist_id and self.order_id.partner_id:
            if (
                self.product_id.rented_product_id
                and self.order_id.pricelist_id.is_interval_pricelist
            ):
                self._check_interval_price()
                self.product_uom_qty = self.rental_qty
                product = self.product_id.with_context(
                    lang=self.order_id.partner_id.lang,
                    partner=self.order_id.partner_id,
                    quantity=self.number_of_time_unit,
                    date=self.order_id.date_order,
                    pricelist=self.order_id.pricelist_id.id,
                    uom=self.product_uom.id,
                    fiscal_position=self.env.context.get("fiscal_position"),
                )

                _logger.info(" %s" % self._get_display_price())

                self.price_unit = self.env[
                    "account.tax"
                ]._fix_tax_included_price_company(
                    self._get_display_price(),
                    product.taxes_id,
                    self.tax_id,
                    self.company_id,
                )

    def _get_product_rental_uom_ids(self):
        self.ensure_one()
        time_uoms = self._get_time_uom()
        res = []
        if self.order_id.pricelist_id.is_interval_pricelist:
            if self.display_product_id.rental_of_interval:
                res = [time_uoms["interval"].id]
        else:
            res = super()._get_product_rental_uom_ids()
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        uom_interval = self.env.ref("rental_pricelist_interval.product_uom_interval")
        super()._onchange_product_id()
        for line in self:
            if (
                line.order_id.pricelist_id.is_interval_pricelist
                and line.product_id
                and line.product_id.rented_product_id
                and line.product_id.rented_product_id.rental_of_interval
            ):
                if line.display_product_id.rental:
                    if line.product_uom.id not in uom_interval.ids:
                        line.product_uom = uom_interval.ids[0]
        return True

    @api.onchange("product_id", "rental_qty")
    def rental_product_id_change(self):
        super().rental_product_id_change()
        self._update_interval_price()
        return True

    @api.onchange("rental_qty", "number_of_time_unit", "product_id")
    def rental_qty_number_of_days_change(self):
        super().rental_qty_number_of_days_change()
        self._update_interval_price()
        return True

    @api.onchange("product_uom", "product_uom_qty")
    def _onchange_product_uom(self):
        super()._onchange_product_uom()
        self._update_interval_price()
        return True

    @api.onchange("start_date", "end_date", "product_uom")
    def _onchange_start_end_date(self):
        super()._onchange_start_end_date()
        if self.start_date and self.end_date:
            self._update_interval_price()
        return True
