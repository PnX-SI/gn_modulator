import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";

import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"
import { WidgetLibraryService } from '@ajsf/core';;
import { AuthService } from "@geonature/components/auth/auth.service";

import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { BaseComponent } from "./base.component";
import { additionalWidgets } from './form'

import utils from "../../utils"

@Component({
  selector: "modules-base-filters",
  templateUrl: "base-filters.component.html",
  styleUrls: ["base-filters.component.scss"],
})
export class BaseFiltersComponent extends BaseComponent implements OnInit {
  additionalWidgets = additionalWidgets;
  dataSource = null;
  displayedColumns = null;

  filterValues = {};
  processedLayout = {};
  dataSave = {}


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
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _mForm: ModulesFormService,
    _router: Router,
    _mRoute: ModulesRouteService,
    _auth: AuthService,
    private _widgetLibraryService: WidgetLibraryService,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute, _auth)
    this._name = 'BaseFilters';
    this.processedEntries = ['schemaName']
  }

  ngOnInit() {
    for (const [key, AdditionalWidget] of Object.entries(additionalWidgets)) {
      this._widgetLibraryService.registerWidget(key, AdditionalWidget);
    }

  }

  processConfig(): void {
    this.processedLayout = this._mForm.processLayout(utils.copy(this.schemaConfig.filters.form.layout))
  }

  getFilters() {
    const filterDefs = this.schemaConfig.filters.defs;
    return Object.entries(this.filterValues)
      .filter(([key, value]) => ![null, undefined].includes(value))
      .map(([key, value]) => ({
          field: filterDefs[key].field,
          type: filterDefs[key].filter_type,
          value
      }))
  }

  onSubmit(event) {
    this.emitEvent({
      action: 'filters',
      params: {
        filters: this.getFilters()
      }
    })

  }

  onFormChanges(event) {
  }

  onIsValid(event) {

  }

  onValidationErrors(event) {}



}