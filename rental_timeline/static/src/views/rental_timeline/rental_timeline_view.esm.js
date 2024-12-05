/** @odoo-module **/

import {RentalTimelineRenderer} from "./rental_timeline_renderer.esm";
import {RentalTimelineModel} from "./rental_timeline_model.esm";
import {registry} from "@web/core/registry";
import {TimelineView} from "@web_timeline/views/timeline/timeline_view.esm";
import {_lt} from "@web/core/l10n/translation";

const viewRegistry = registry.category("views");

export const RentalTimelineView = {
    ...TimelineView,
    display_name: _lt("Rental Timeline"),
    Model: RentalTimelineModel,
    Renderer: RentalTimelineRenderer,
};

viewRegistry.add("rental_timeline", RentalTimelineView);
