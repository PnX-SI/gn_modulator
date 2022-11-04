import { Component, OnInit, Injector } from '@angular/core';
import { ModulesConfigService } from '../services/config.service';
import { ModulesPageService } from '../services/page.service';
import { ModulesDataService } from '../services/data.service';
import { ModulesLayoutService } from '../services/layout.service';
import { AuthService, User } from '@geonature/components/auth/auth.service';
import { ActivatedRoute } from '@angular/router';
import { mergeMap } from '@librairies/rxjs/operators';
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
  _auth: AuthService;
  _mLayout: ModulesLayoutService;
  _mData: ModulesDataService;

  debug = false; // pour activer le mode debug (depuis les queryParams)

  routeParams; // paramètre d'url
  routeQueryParams; // query params
  moduleParams; // paramètre du module

  // moduleConfig; // configuration du module
  // pageConfig; // configuration de la route en cours
  // moduleCode; // code du module en cours

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
    // reset de page service (breadcrump etc .....)
    this._mPage.reset();

    // récupération de l'utilisateur courant
    this._mPage.currentUser = this._auth.getCurrentUser();

    // - on le place dans layout.meta pour pouvoir s'en servir dans le calcul des layouts
    this._mLayout.meta['currentUser'] = this._mPage.currentUser;

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
          this.moduleParams = this._mPage.moduleConfig.params || {};
          this.processParams();
          return this._mPage.getBreadcrumbs();
        })
      )
      .subscribe(() => {
        this.pageInitialized = true;
      });
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

    this._mPage.moduleCode = routeData.moduleCode;

    // recupéraiton de la configuration de la page;
    this._mPage.moduleConfig = this._mConfig.moduleConfig(this._mPage.moduleCode);
    this._mPage.pageName = routeData.pageName;
    this._mPage.pageConfig = this._mPage.moduleConfig.pages[routeData.pageName];

    // initialisatio du layout
    this.layout = {
      layout_name: this._mPage.pageConfig.layout_name,
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
      ...this.moduleParams,
    };

    // pour pouvoir accéder au paramètres pour le calcul des layouts
    this._mLayout.meta['params'] = this._mPage.params;

    let objectsModule = utils.copy(this._mPage.moduleConfig.objects);
    const objectsPage = utils.copy(this._mPage.pageConfig.objects || {});

    // gestion du paramètre debug
    this.debug = ![undefined, false, 'false'].includes(this.routeQueryParams.debug);
    // pour toutes les clés de data (moduleConfig.objects)
    for (const [objectName, objectConfig] of Object.entries(objectsModule) as any) {
      // on ajoute les données data définies pour la page
      // par exemple typeKey  = value|filters|prefilters
      const objectsPageValue = objectsPage[objectName];
      if (!objectsPageValue) {
        continue;
      }
      for (const [typeKey, typeValue] of Object.entries(objectsPageValue)) {
        objectConfig[typeKey] = typeValue;
      }
    }

    // prise en comptes des routeParams et routeQueryParams
    // par exemple on va remplacer ':id_site' par la valeurs indexée par la clé id_site
    // dans le dictionnaire params crée à partir des paramètre des routes (urlParams + queryParams)

    for (const [paramKey, paramValue] of Object.entries(this._mPage.params)) {
      objectsModule = utils.replace(objectsModule, `:${paramKey}`, paramValue);
    }

    // pour communiquer les données aux composants du layout
    this.data = objectsModule;

    // resize des composants
    // TODO à affiner
    // setTimeout(() => this._mLayout.reComputeHeight('page'), 500);
  }

  /**
   * TODO clarifier les process actions un peu partout
   */
  processAction(event) {
    const data = event.layout.key ? event.data[event.layout.key] : event.data;
    if (['submit', 'cancel', 'edit', 'details', 'create'].includes(event.action)) {
      this._mPage.processAction({
        action: event.action,
        objectName: data.object_name,
        data: data,
        layout: event.layout,
      });
    }
  }
}
