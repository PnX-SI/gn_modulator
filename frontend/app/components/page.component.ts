import { Component, OnInit, Injector } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";
import { ModulesPageService } from "../services/page.service";
import { ModulesDataService } from "../services/data.service";
import { ModulesLayoutService } from "../services/layout.service";
import { AuthService, User } from "@geonature/components/auth/auth.service";
import { ActivatedRoute } from "@angular/router";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { of, forkJoin } from "@librairies/rxjs";

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
  _mData: ModulesDataService

  currentUser: User; // utilisateur courant

  debug = false; // pour activer le mode debug (depuis les queryParams)

  routeParams; // paramètre d'url
  routeQueryParams; // query params

  moduleParams; // paramètre du module

  moduleConfig; // configuration du module
  pageConfig; // configuration de la route en cours
  moduleCode; // code du module en cours
  layout; // layout de la page (récupéré depuis pageConfig.layout_name)
  data; // data pour le layout

  pageInitialized: boolean; // test si la page est initialisée (pour affichage)

  constructor(private _injector: Injector) {
    this._route = this._injector.get(ActivatedRoute);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mData = this._injector.get(ModulesDataService);
    this._mPage = this._injector.get(ModulesPageService);
    this._auth = this._injector.get(AuthService);
    this._mLayout = this._injector.get(ModulesLayoutService);
  }

  ngOnInit() {

    // récupération de l'utilisateur courant
    this.currentUser = this._auth.getCurrentUser();

    // - on le place dans layout.meta pour pouvoir s'en servir dans le calcul des layouts
    this._mLayout.meta['currentUser'] = this.currentUser;


    // reset du breadcrumb
    this._mPage.breadcrumbs = [];

    // process
    // - route data
    // - route params
    // - route query params
    // - breadcrumbs
    this._route.data
      .pipe(
        // route data
        mergeMap((routeData) => {
          this.processRouteData(routeData);
          return this._route.params;
        }),
        // url params
        mergeMap((params) => {
          this.routeParams = params;
          return this._route.queryParams;
        }),
        // url queryParams
        mergeMap((queryParams) => {
          this.routeQueryParams = queryParams;
          return this.getModuleParams();
        }),
        // moduile params
        mergeMap((moduleParams) => {
          this.moduleParams = moduleParams;
          this.processParams();
          return this._mPage.getBreadcrumbs();
        })
      )
      .subscribe(() => {
        this.pageInitialized = true;
      });
  }

  /**
   * Pour récupérer des données comme
   * un id_module à partir d'un module_code
   */
  getModuleParams() {

    if (!this.moduleConfig.params) {
      return of({})
    }

    const moduleParams = {};

    const moduleParamsConfig: any = this.moduleConfig.params || {};

    // dictionnaire des observable pour le forkJoin
    const getOnes = {}

    // traitement de chaque paramètre à résoudre
    for (const [keyParam, paramConfig] of Object.entries(moduleParamsConfig)) {
      const schemaName = (paramConfig as any).schema_name || this.moduleConfig.data[(paramConfig as any).object_name].schema_name;
      const fieldName = (paramConfig as any).field_name;
      const value = (paramConfig as any).value;
      const fields = (paramConfig as any).fields || keyParam;
      getOnes[keyParam] = this._mData.getOne(schemaName, value, {field_name: fieldName, fields})
    }

    return forkJoin(getOnes)
      .pipe(
        concatMap((res) => {
          for (const [resKey, resValue] of Object.entries(res)) {
            const keyValue = Object.keys(resValue as any)[0]
            moduleParams[resKey] = (resValue as any)[keyValue];
          }
          
          return of(moduleParams);
        })
      )

  }

  /**
   * analyse des données fournies par la route
   *  - pageName
   *  - moduleCode
   * afin de récupérer
   *  - la config du module
   *  - la config de la page
   *  - et le layout correspondant
   */
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
  processParams() {

    this._mPage.params = {
      ...this.routeQueryParams,
      ...this.routeParams,
      ...this.moduleParams
    }

    // pour pouvoir accéder au paramètres pour le calcul des layouts
    this._mLayout.meta['params'] = this._mPage.params;

    let data = utils.copy(this.moduleConfig.data);
    const dataPage = utils.copy(this.pageConfig.data || {});

    // gestion du paramètre debug
    this.debug = ![undefined, false, "false"].includes(
      this.routeQueryParams.debug
    );

    // pour toutes les clés de data (moduleConfig.data)
    for (const [objectName, objectConfig] of Object.entries(data)) {
      // set object_name
      (objectConfig as any).object_name = objectName;

      // on ajoute les données data définies pour la page
      // par exemple typeKey  = value|filters|prefilters
      const dataPageValue = dataPage[objectName];
      if (!dataPageValue) {
        continue;
      }
      for (const [typeKey, typeValue] of Object.entries(dataPageValue)) {
        (objectConfig as any)[typeKey] = typeValue;
      }
    }

    // prise en comptes des routeParams et routeQueryParams
    // par exemple on va remplacer ':id_site' par la valeurs indexée par la clé id_site
    // dans le dictionnaire params crée à partir des paramètre des routes (urlParams + queryParams)


    for (const [paramKey, paramValue] of Object.entries(this._mPage.params)) {
      data = utils.replace(data, `:${paramKey}`, paramValue);
    }

    // pour communiquer les données aux composants du layout
    this.data = data;

    // resize des composants
    // TODO à affiner
    // setTimeout(() => this._mLayout.reComputeHeight('page'), 500);
  }

  /**
   * TODO clarifier les process actions un peu partout
   */
  processAction(event) {
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
