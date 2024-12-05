# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalTimeline(RentalStockCommon):
    def setUp(self):
        super().setUp()
        ProductObj = self.env["product.product"]
        self.partnerA = self.PartnerObj.create(
            {
                "name": "Timeline Partner A",
                "country_id": self.env.ref("base.de").id,
            }
        )
        self.product_rental_1 = ProductObj.create(
            {
                "name": "Rental Product Timeline 1",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        self.product_rental_2 = ProductObj.create(
            {
                "name": "Rental Product Timeline 2",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        self.product_rental_3 = ProductObj.create(
            {
                "name": "Rental Product Timeline 3",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        # dates
        self.date_0101 = fields.Date.from_string("2022-01-01")
        self.date_0110 = fields.Date.from_string("2022-01-10")
        self.date_0102 = fields.Date.from_string("2022-01-02")
        self.date_0111 = fields.Date.from_string("2022-01-11")
        self.service_rental = self.env["product.product"]

    def get_related_timeline_from_rental_order(self, line):
        domain = [
            ("res_model", "=", "sale.order.line"),
            ("res_id", "in", line.ids),
        ]
        TimelineObj = self.env["product.timeline"]
        timeline = TimelineObj.search(domain)
        return timeline

    def test_00_update_partner_rental_order(self):
        # rental service product
        self.service_rental = self._create_rental_service_day(self.product_rental_1)
        # rental order
        rental_order_1 = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
            product=self.service_rental,
        )
        rental_order_1.action_confirm()
        self.assertEqual(len(rental_order_1.order_line), 1)
        line = rental_order_1.order_line[0]
        self.assertEqual(line.product_id, self.service_rental)
        self.assertEqual(rental_order_1.partner_id.name, self.partnerA.name)
        # get related timeline object
        timeline = self.get_related_timeline_from_rental_order(line)
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline.partner_id.name, self.partnerA.name)
        # update Partner A name
        self.partnerA.name = "Timeline Partner A Update"
        # check partner name on Rental Order and Rental Timeline
        self.assertEqual(rental_order_1.partner_id.name, self.partnerA.name)
        self.assertEqual(timeline.partner_id.name, self.partnerA.name)

    def test_02_change_state_of_rental_order(self):
        # rental service product
        self.service_rental = self._create_rental_service_day(self.product_rental_3)
        # rental order
        rental_order_3 = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
            product=self.service_rental,
        )
        rental_order_3.action_confirm()
        self.assertEqual(len(rental_order_3.order_line), 1)
        line = rental_order_3.order_line[0]
        # get related timeline object
        timeline = self.get_related_timeline_from_rental_order(line)
        # cancel order
        rental_order_3.action_cancel()
        # set to draft order
        rental_order_3.action_draft()
        # get related timeline object after set to draft the order
        timeline = self.get_related_timeline_from_rental_order(line)
        self.assertTrue(timeline)
