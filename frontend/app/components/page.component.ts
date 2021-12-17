import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";
// import { ModulesRouteService } from "../services/route.service";
import { ActivatedRoute } from "@angular/router";
import { Routes,  RouterModule, Router } from "@angular/router";

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
    private _router: Router,
    // private _mRoute: ModulesRouteService
  ) {
  }

  routeData;
  pageConfig;
  pageName;
  moduleName;
  actions;
  breadcrumbs = [];

  ngOnInit() {
    this._route.data.subscribe((routeData) => {
      this.routeData = routeData
      this.pageName = this.routeData.pageName;
      this.moduleName = this.routeData.moduleName;
      this.pageConfig = this._mConfig.moduleConfig(this.moduleName).pages[this.pageName]
      this.actions = this._mConfig.moduleConfig(this.moduleName).actions
      this.setBreadcrumbs();
    })
    this._route.params.subscribe((params) => {
      this.value = params.value;
      this.setBreadcrumbs();
  });

    this._route.queryParams.subscribe((params) => {
        this.debug = ![undefined, false, 'false'].includes(params.debug);
    });
  }

  setBreadcrumbs() {
    this.breadcrumbs = []
    console.log(this.pageConfig)
    if(this.pageConfig.parent) {
      const parentPageConfig = this._mConfig.moduleConfig(this.moduleName).pages[this.pageConfig.parent.pageName]
      this.breadcrumbs.push({
        txt: parentPageConfig.label,
        url: this.modulePageUrl(this.moduleName, this.pageConfig.parent.pageName, {})
      });
    }

    this.breadcrumbs.push({
      txt: `${this.pageConfig.label} ${this.value || ''}`
    })
    console.log('uutuutu')
  }

  modulePageUrl(moduleName, pageName, params) {
    const moduleConfig = this._mConfig.moduleConfig(moduleName);
    const pageConfig = moduleConfig.pages[pageName];
    var url = pageConfig.url;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, value)
    }
    return `#/modules/${moduleConfig.code.toLowerCase()}/${url}`
  }

  navigateToPage(moduleName, pageName, params) {
    const url = this.modulePageUrl(moduleName, pageName, params);

    // patch sinon navigateByUrl met des plombes...
    const baseUrl = window.location.href.replace(this._router.url, '')
    window.location.href = baseUrl + url;
  }

  breadcrumbNavigateToPage(breadcrumb: any) {
    this.navigateToPage(this.moduleName, this.breadcrumbs['pageName'], this.breadcrumbs['params'])
  }
}
