import { Component, OnInit, Injector } from '@angular/core';
import { ModulesConfigService } from '../services/config.service';
import { ModulesPageService } from '../services/page.service';
import { ModulesDataService } from '../services/data.service';
import { ModulesLayoutService } from '../services/layout.service';
import { ModulesContextService } from '../services/context.service';
import { AuthService, User } from '@geonature/components/auth/auth.service';
import { ActivatedRoute } from '@angular/router';
import { mergeMap } from '@librairies/rxjs/operators';
import { of } from '@librairies/rxjs';
import utils from '../utils';

@Component({
  selector: 'modules-page',
  templateUrl: 'page.component.html',
  styleUrls: ['base/base.scss', 'page.component.scss'],
})
export class PageComponent implements OnInit {
  // services
  _mConfig: ModulesConfigService;
  _route: ActivatedRoute;
  _mPage: ModulesPageService;
  _mLayout: ModulesLayoutService;
  _mData: ModulesDataService;
  _mContext: ModulesContextService;

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

  moduleCode;
  pageCode;
  params;

  constructor(private _injector: Injector) {
    this._route = this._injector.get(ActivatedRoute);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mData = this._injector.get(ModulesDataService);
    this._mPage = this._injector.get(ModulesPageService);
    this._mLayout = this._injector.get(ModulesLayoutService);
    this._mContext = this._injector.get(ModulesContextService);
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
    this._mConfig
      .init()
      .pipe(
        mergeMap(() => {
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
          setTimeout(()=> this._mLayout.reComputeLayout(''), 100);
          this.moduleParams = this._mConfig.moduleConfig(this.moduleCode).params || {};
          this.params = {
            ...this.routeQueryParams,
            ...this.routeParams,
            ...this.moduleParams,
          };



          this._mContext.initContext({
            module_code: this.moduleCode,
            page_code: this.pageCode,
            params: this.params,
          });
          return of(true);
        })
      )
      .subscribe(() => {
        this.pageInitialized = true;
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
  // processAction(event) {
  //   const data = event.layout.key ? event.data[event.layout.key] : event.data;
  //   if (['submit', 'cancel', 'edit', 'details', 'create'].includes(event.action)) {
  //     this._mPage.processAction({
  //       action: event.action,
  //       context: this.context,
  //       data: data,
  //       layout: event.layout,
  //     });
  //   }
  // }
}
