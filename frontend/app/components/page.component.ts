import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";
import { ActivatedRoute } from "@angular/router";

@Component({
  selector: "modules-page",
  templateUrl: "page.component.html",
  styleUrls: ["base/base.scss", "page.component.scss"],
})
export class PageComponent implements OnInit {

  debug=false
  value;

  constructor(
    private _mConfig: ModulesConfigService,
    private _route: ActivatedRoute,
  ) {
  }

  routeData;
  pageConfig;
  pageName;
  moduleName;

  ngOnInit() {
    this._route.data.subscribe((routeData) => {
      this.routeData = routeData
      this.pageName = this.routeData.pageName;
      this.moduleName = this.routeData.moduleName;
      this.pageConfig = this._mConfig.moduleConfig(this.moduleName).pages[this.pageName]
    })
    this._route.params.subscribe((params) => {
      this.value = params.value;
  });

    this._route.queryParams.subscribe((params) => {
        this.debug = ![undefined, false, 'false'].includes(params.debug);
    });
  }

}
