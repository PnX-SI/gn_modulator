import { Component, OnInit, Injector } from "@angular/core";
import { ModulesLayoutObjectComponent } from "./layout-object.component";
import utils from "../../../utils";

@Component({
  selector: "modules-layout-object-filters",
  templateUrl: "layout-object-filters.component.html",
  styleUrls: ["../../base/base.scss", "layout-object-filters.component.scss"],
})
export class ModulesLayoutObjectFiltersComponent
  extends ModulesLayoutObjectComponent
  implements OnInit
{
  filterValues: any = {};


  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-object-filters";
  }

  processConfig(): void {
    this.processedLayout = {
      height_auto: true,
      type: "form",
      appearance: "outline",
      items: [
        {
          title: "Filtres",
          flex: "0",
        },
        {
          items: this.schemaConfig.filters.form.layout,
          overflow: true,
        },
        {
          flex: "0",
          direction: "row",
          items: [
            {
              flex: "0",
              type: "button",
              color: "primary",
              title: "Rechercher",
              description:
                "Effectuer une recherche avec les filtre définis ci-dessus",
              action: "filter",
            },
            {
              flex: "0",
              type: "button",
              color: "primary",
              title: "Réinitialiser",
              description: "RAZ des filtres",
              action: "clear-filters",
            },
          ],
        },
      ],
    };
  }

  processAction(event) {
    event.action == "filter" && this.applyFilters();
    event.action == "clear-filters" && this.clearFilters();
  }

  getFilters() {
    const filterDefs = this.schemaConfig.filters.defs;
    return Object.entries(this.filterValues)
      .filter(([key, value]) => ![null, undefined].includes(value))
      .map(([key, value]) => ({
        field: filterDefs[key].field,
        type: filterDefs[key].filter_type,
        value: filterDefs[key].key ? value[filterDefs[key].key] : value,
      }));
  }

  applyFilters() {
    this._mObject.setObjectValue(this.schemaName(), "filters", this.getFilters());
  }

  clearFilters() {
    for (const key of Object.keys(this.filterValues)) {
      this.filterValues[key] = null;
    }
    const filterValues = utils.copy(this.filterValues);
    this.filterValues = null;
    setTimeout(() => {
      this.filterValues = filterValues;
      this.applyFilters();
    });
  }
}
