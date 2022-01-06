import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { WidgetLibraryService } from 'angular7-json-schema-form';
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesRouteService } from "../../services/route.service"
import { AuthService } from "@geonature/components/auth/auth.service";

import { BaseComponent } from "./base.component";

@Component({
  selector: "modules-page-element",
  templateUrl: "page-element.component.html",
  styleUrls: ["base.scss", "page-element.component.scss"],
})
export class PageElementComponent extends BaseComponent implements OnInit  {

    @Input() elementType: string;

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
    ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute, _auth)
    this._name="PageElement"
    };

    ngOnInit() {
    }

    onComponentInitialized() {
    }

    processEvent(event) {

      const action = this.actions[event.action]

      if (!action) {
        return;
      }

      if(action.type == 'link') {
        return this._mRoute.navigateToPage(this.moduleName, action.pageName, event.params)
      }


    }

}