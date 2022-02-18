import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"
import { AuthService } from "@geonature/components/auth/auth.service";
import { ModulesService } from "../../services/all.service";

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
  arrayLayout;
  arrayData;

  @Input() direction;

constructor(
  _services: ModulesService
) {
  super(_services)
  this._name = 'BaseLayout';
}

  ngOnInit() {
    this.checkLayout(this.layout);
  }

  checkLayout(layout) {
    this.layoutType = this._services.mLayout.getLayoutType(layout)
    if(['key', 'array'].includes(this.layoutType)) {
      this.data = this.layoutData[this.layout.key || this.layout];
      this.layoutTxt = `${this.data.label} : ${this.data.value}`
    }

    // on enlève les []
    if (this.layoutType == 'array'){
      this.arrayLayout = this._services.mLayout.removeBrakets(this.layout.items)
      this.arrayData = this.data.value
        .map(d =>
          this._services.mLayout.getLayoutData(
            this.arrayLayout,
            d
          )
        );
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