import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesMapService } from "../../services/map.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"

import { CommonService } from "@geonature_common/service/common.service";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { BaseComponent } from "./base.component";

@Component({
  selector: "modules-map-list",
  templateUrl: "map-list.component.html",
  styleUrls: [ "base.scss", "map-list.component.scss", ],
})
export class ModulesMapListComponent extends BaseComponent implements OnInit {


  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _mForm: ModulesFormService,
    _router: Router,
    _mRoute: ModulesRouteService,
    ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute)
    this._name = 'MapList'
  }

  ngOnInit(): void {
    this.setFullHeight();
  }

  processEvent(event) {

    this.emitEvent(event);

    if(event.action == 'filters') {
      this.filters = event.params.filters;
    }

    if(event.action == 'selected') {
      this.value = event.params.value
    }

  }

}