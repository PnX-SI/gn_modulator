import { Component, OnInit } from "@angular/core";

import { ModulesService } from "../../services/all.service";
import { WidgetLibraryService } from "@ajsf/core";

import { BaseComponent } from "./base.component";
import { additionalWidgets } from "./form";

import utils from "../../utils";

@Component({
  selector: "modules-base-filters",
  templateUrl: "base-filters.component.html",
  styleUrls: ["./base.scss", "base-filters.component.scss"],
})
export class BaseFiltersComponent extends BaseComponent implements OnInit {
  additionalWidgets = additionalWidgets;
  dataSource = null;
  displayedColumns = null;

  filterValues = {};
  processedLayout = {};
  dataSave = {};

  // dataFilters = {
  //   "filters": [
  //     {
  //       "field": "id_pf",
  //       "type": "like",
  //       "value": "11"
  //     }
  //   ]
  // }

  constructor(
    _services: ModulesService,
    private _widgetLibraryService: WidgetLibraryService
  ) {
    super(_services);
    this._name = "BaseFilters";
    this.processedEntries = ["schemaName"];
  }

  ngOnInit() {
    for (const [key, AdditionalWidget] of Object.entries(additionalWidgets)) {
      this._widgetLibraryService.registerWidget(key, AdditionalWidget);
    }
  }

  processConfig(): void {
    this.processedLayout = this.schemaConfig.filters.form.layout;
  }

  getFilters() {
    const filterDefs = this.schemaConfig.filters.defs;
    return Object.entries(this.filterValues)
      .filter(([key, value]) => ![null, undefined].includes(value))
      .map(([key, value]) => ({
        field: filterDefs[key].field,
        type: filterDefs[key].filter_type,
        value: filterDefs.key ? value[filterDefs.key]: value,
      }));
  }

  onSubmit() {
    this._services.schema.get(this.schemaName).filters = this.getFilters();
    this.emitEvent({
      action: "filters",
      params: {
        filters: this.getFilters(),
      },
    });
  }

  onReinit() {
    for (const key of Object.keys(this.filterValues)) {
      this.filterValues[key] = null;
    }
    const filterValues = utils.copy(this.filterValues);
    this.filterValues = null;
    setTimeout(() => {
      this.filterValues = filterValues;
      this.onSubmit();
    });
  }

  onFormChanges(event) {}

  onIsValid(event) {}

  onValidationErrors(event) {}
}
