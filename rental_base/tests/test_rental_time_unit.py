# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo.tests import Form

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalTimeUnit(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("uom.group_uom")
        cls.uom_week = cls.env.ref("rental_base.product_uom_week")
        cls.product_rental = cls.env["product.product"].create(
            {
                "name": "Rental Product",
                "type": "product",
                "categ_id": cls.category_all.id,
            }
        )
        cls.service_rental = cls._create_rental_service_day(product=cls.product_rental)

    def _rental_line_qty(self, start_date, end_date, uom):
        order_form = Form(self.env["sale.order"])
        order_form.type_id = self.rental_sale_type
        order_form.partner_id = self.partnerA
        with order_form.order_line.new() as line:
            line.product_id = self.service_rental
            line.rental_qty = 2
            line.start_date = start_date
            line.end_date = end_date
            line.product_uom = uom
            return line.product_uom_qty

    def test_rental_qty_in_days(self):
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-01-10", self.uom_day), 20
        )

    def test_rental_qty_in_weeks_counts_started_weeks(self):
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-01-14", self.uom_week), 4
        )
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-01-15", self.uom_week), 6
        )

    def test_rental_qty_in_months_counts_started_months(self):
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-01-10", self.uom_month), 2
        )
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-01-31", self.uom_month), 2
        )
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-03-01", self.uom_month), 6
        )

    def test_rental_qty_in_hours_follows_company_calendar(self):
        calendar = self.env["resource.calendar"].create(
            {
                "name": "Six hours a day",
                "attendance_ids": [(5, 0, 0)]
                + [
                    (
                        0,
                        0,
                        {
                            "name": "Morning",
                            "dayofweek": str(day),
                            "hour_from": 8,
                            "hour_to": 14,
                        },
                    )
                    for day in range(5)
                ],
            }
        )
        self.env.company.resource_calendar_id = calendar
        self.assertEqual(
            self._rental_line_qty("2021-01-01", "2021-01-02", self.uom_hour), 24
        )
