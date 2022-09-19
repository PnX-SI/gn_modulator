import { Component, OnInit, Injector } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";
import { ModulesPageService } from "../services/page.service";
import { ModulesLayoutService } from "../services/layout.service";
import { AuthService, User } from "@geonature/components/auth/auth.service";
import { ActivatedRoute } from "@angular/router";
import { mergeMap } from "@librairies/rxjs/operators";
import { of } from "@librairies/rxjs";

import utils from "../utils";

@Component({
  selector: "modules-page",
  templateUrl: "page.component.html",
  styleUrls: ["base/base.scss", "page.component.scss"],
})
export class PageComponent implements OnInit {
  // services
  _mConfig: ModulesConfigService;
  _route: ActivatedRoute;
  _mPage: ModulesPageService;
  _auth: AuthService;
  _mLayout: ModulesLayoutService

  currentUser: User;

  debug = false; // pour activer le mode debug (depuis les queryParams)

  routeParams; // paramètre d'url
  routeQueryParams; // query params

  moduleConfig; // configuration du module
  pageConfig; // configuration de la route en cours
  moduleCode; // code du module en cours
  layout; // layout de la page (récupéré depuis pageConfig.layout_name)
  data; // data pour le layout

  pageInitialized: boolean; // test si la page est initialisée (pour affichage)

  constructor(private _injector: Injector) {
    this._route = this._injector.get(ActivatedRoute);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mPage = this._injector.get(ModulesPageService);
    this._auth = this._injector.get(AuthService);
    this._mLayout = this._injector.get(ModulesLayoutService);
  }

  ngOnInit() {

    this.currentUser = this._auth.getCurrentUser();
    const layoutMeta = this._mLayout.meta();
    layoutMeta['currentUser'] = this.currentUser;
    this._mPage.breadcrumbs = [];

    this._route.data
      .pipe(
        mergeMap((routeData) => {
          this.processRouteData(routeData);
          return this._route.params;
        }),
        mergeMap((params) => {
          this.routeParams = params;
          return this._route.queryParams;
        }),
        mergeMap((queryParams) => {
          this.routeQueryParams = queryParams;
          this.processRouteParams();
          return of(true);
        }),
        mergeMap(() => {
          return this._mPage.getBreadcrumbs();
        })
      )
      .subscribe(() => {
        this.pageInitialized = true;
      });
  }

  processRouteData(routeData) {
    // reset data
    this.data = null;

    this._mPage.setCurrentPage(routeData.pageName);
    this.moduleCode = routeData.moduleCode;

    // pour pouvoir retrouver moduleCode par ailleurs
    this._mPage.moduleCode = routeData.moduleCode;

    // recupéraiton de la configuration de la page;
    this.moduleConfig = this._mConfig.moduleConfig(this.moduleCode);
    this.pageConfig = this.moduleConfig.pages[this._mPage.pageName];

    // initialisatio du layout
    this.layout = {
      layout_name: this.pageConfig.layout_name,
    };
  }

  // lien entre les paramètres
  // en passant par data
  // permet de récupérer value
  // - id de l'objet en cours ? (par ex. id d'un site)
  // - paramètre de prefilter pour des liste d'objet (par ex. visite d'un site)
  processRouteParams() {

    this._mPage.pageAllParams = {
      ...this.routeQueryParams,
      ...this.routeParams
    }
    this._mPage.pageParams = this.routeParams;
    this._mPage.pageQueryParams = this.routeQueryParams;

    let data = utils.copy(this.moduleConfig.data);
    const dataPage = utils.copy(this.pageConfig.data || {});

    this.debug = ![undefined, false, "false"].includes(
      this.routeQueryParams.debug
    );



    // pour toutes les clés de data (moduleConfig.data)
    for (const [dataKey, dataValue] of Object.entries(data)) {
      // set object_name
      (dataValue as any).object_name = dataKey;

      // on ajoute les données data définies pour la page
      const dataPageValue = dataPage[dataKey];
      if (!dataPageValue) {
        continue;
      }
      for (const [typeKey, typeValue] of Object.entries(dataPageValue)) {
        (dataValue as any)[typeKey] = typeValue;
      }
    }

    // prise en comptes des routeParams et routeQueryParams
    for (const [paramKey, paramValue] of Object.entries(this.routeParams)) {
      data = utils.replace(data, `:${paramKey}`, paramValue);
    }

    for (const [paramKey, paramValue] of Object.entries(
      this.routeQueryParams
    )) {
      data = utils.replace(data, `:${paramKey}`, paramValue);
    }

    // pour communiquer ses données aux composants du layout
    this.data = data;

    // resize des composants
    setTimeout(() => this._mLayout.reComputeHeight('page'), 100);
    setTimeout(() => this._mLayout.reComputeHeight('page'), 500);
  }

  /**
   * TODO clarifier les process actions un peu partout
   */
  processAction(event) {
    console.log('page Action', event);
    const data = event.layout.key ? event.data[event.layout.key] : event.data;
    if (
      ["submit", "cancel", "edit", "details", "create"].includes(event.action)
    ) {
      this._mPage.processAction({
        action: event.action,
        objectName: data.object_name,
        schemaName: data.schema_name,
        data: data,
        layout: event.layout,
      });
    }
  }
}
