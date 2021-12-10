import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"

import { BaseComponent } from "./base.component";
import utils from '../../utils'

@Component({
  selector: "modules-base-layout",
  templateUrl: "base-layout.component.html",
  styleUrls: ["base.scss", "base-layout.component.scss"],
})
export class BaseLayoutComponent extends BaseComponent implements OnInit {

  layoutType;
  layoutTxt;

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
  this._name = 'BaseLayout';
}

  ngOnInit() {
    this.checkLayout(this.layout);
  }

  checkLayout(layout) {
    this.layoutType = this.getLayoutType(layout)
    if(this.layoutType == 'key') {
      this.data = this.layoutData[this.layout];
      // const data = this.layoutData[this.layout];
      this.layoutTxt = `${this.data.label} : ${this.data.value}`
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {

      if(utils.fastDeepEqual(change['currentValue'], change['previousValue'])) {
        continue;
      }

      if(key == 'layout') {
        this.checkLayout(change['currentValue']);
      }
    }
  }

}