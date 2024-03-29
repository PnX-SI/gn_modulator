import { Component, OnInit, Injector } from '@angular/core';
import { ModulesConfigService } from '../services/config.service';
import { ModulesDataService } from '../services/data.service';
import { ModulesLayoutService } from '../services/layout.service';
import { ModulesContextService } from '../services/context.service';
import { ModulesActionService } from '../services/action.service';
import { ModulesNomenclatureService } from '../services/nomenclature.service';
import { ModuleService } from '@geonature/services/module.service';
import { ActivatedRoute } from '@angular/router';
import { mergeMap } from '@librairies/rxjs/operators';
import { of } from '@librairies/rxjs';

@Component({
  selector: 'modules-page',
  templateUrl: 'page.component.html',
  styleUrls: ['base/base.scss', 'page.component.scss'],
})
export class PageComponent implements OnInit {
  // services
  _mConfig: ModulesConfigService;
  _route: ActivatedRoute;
  _mLayout: ModulesLayoutService;
  _mData: ModulesDataService;
  _mAction: ModulesActionService;
  _mContext: ModulesContextService;
  _gnModuleService: ModuleService;
  _mNomenclature: ModulesNomenclatureService;
  debug = false; // pour activer le mode debug (depuis les queryParams)

  routeParams; // paramètre d'url
  routeQueryParams; // query params
  moduleParams; // paramètre du module

  // moduleConfig; // configuration du module
  // pageConfig; // configuration de la route en cours
  // moduleCode; // code du module en cours

  layout; // layout de la page (récupéré depuis pageConfig.layout_code)
  data; // data pour le layout

  pageInitialized: boolean; // test si la page est initialisée (pour affichage)
  pageAuthorized: boolean; // test si on a au moins les accès en lecture sur le module
  moduleCode;
  pageCode;
  params;

  _sub;
  constructor(private _injector: Injector) {
    this._route = this._injector.get(ActivatedRoute);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mData = this._injector.get(ModulesDataService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._mContext = this._injector.get(ModulesContextService);
    this._mAction = this._injector.get(ModulesActionService);
    this._mNomenclature = this._injector.get(ModulesNomenclatureService);
    this._gnModuleService = this._injector.get(ModuleService);
  }

  ngOnInit() {
    // reset de page service (breadcrump etc .....)

    // - on le place dans layout.meta pour pouvoir s'en servir dans le calcul des layouts

    // process
    // - init config
    // - route data
    // - route params
    // - route query params
    // - breadcrumbs
    this.pageInitialized = false;
    this._sub = this._mConfig
      .init()
      .pipe(
        mergeMap(() => {
          // processRigths

          return this._mNomenclature.init();
        }),
        mergeMap(() => {
          // processRigths

          return this._route.data;
        }),
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
          this.debug = this.routeQueryParams.debug != undefined;
          const moduleConfig = this._mConfig.moduleConfig(this.moduleCode);
          this.moduleParams = moduleConfig.params || {};
          this.params = {
            ...this.routeQueryParams,
            ...this.routeParams,
            ...this.moduleParams,
          };

          if (this.moduleCode) {
            setTimeout(() => {
              this._gnModuleService.currentModule$.next(
                this._gnModuleService.getModule(this.moduleCode),
              );
            });
          }

          this._mContext.initContext({
            module_code: this.moduleCode,
            page_code: this.pageCode,
            params: this.params,
            config: {
              ...(moduleConfig.config_defaults || {}),
              ...(moduleConfig.config_params || {}),
            },
          });
          return of(true);
        }),
      )
      .subscribe(() => {
        const cruved = this._gnModuleService.modules.find(
          (m) => m.module_code == this.moduleCode,
        ).cruved;
        this.pageInitialized = true;
        this.pageAuthorized = !!cruved.R;
      });
  }

  /**
   * analyse des données fournies par la route
   *  - pageCode
   *  - moduleCode
   * afin de récupérer
   *  - la config du module
   *  - la config de la page
   *  - et le layout correspondant
   */
  processRouteData(routeData) {
    // reset data
    this.data = null;

    this.moduleCode = routeData.moduleCode;

    // recupéraiton de la configuration de la page;
    this.pageCode = routeData.pageCode;

    // initialisation du layout
    this.layout = this._mConfig.pageConfig(routeData.moduleCode, routeData.pageCode).layout;
  }

  /**
   * TODO clarifier les process actions un peu partout
   */
  processAction(event) {
    if (['cancel', 'edit', 'details', 'create'].includes(event.action)) {
      this._mAction.processAction({
        action: event.action,
        context: event.context,
        data: event.data,
        layout: event.layout,
      });
    }
  }

  ngOnDestroy() {
    this._sub && this._sub.unsubscribe();
  }
}
