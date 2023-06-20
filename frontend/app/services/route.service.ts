import { Injectable, Injector } from '@angular/core';

import { of, Subject } from '@librairies/rxjs';
import { mergeMap } from '@librairies/rxjs/operators';
import { ModulesConfigService } from './config.service';
import { CommonService } from '@geonature_common/service/common.service';
import { Router } from '@angular/router';
import { PageComponent } from '../components/page.component';
import utils from '../utils';

@Injectable()
export class ModulesRouteService {
  routesLoaded = false;
  routesLoadedSubject;
  _commonService: CommonService;
  _router: Router;
  _mConfig: ModulesConfigService;

  constructor(private _injector: Injector) {
    // setTimeout(()=> {
    this._mConfig = this._injector.get(ModulesConfigService);
    this._commonService = this._injector.get(CommonService);
    this._router = this._injector.get(Router);
    this.initRoutes().subscribe(() => {});
    // });
  }

  init() {}

  /**
   * initialisation des routes en fonction du retour de l'api '/modules/config'
   * on utilise un subject pour gérer les appels simultanés à initRoute
   */
  initRoutes() {
    if (this.routesLoaded) {
      return of(true);
    }

    if (this.routesLoadedSubject) {
      return this.routesLoadedSubject;
    }

    this.routesLoadedSubject = new Subject<boolean>();

    return this._mConfig.init().pipe(
      mergeMap(() => {
        const modulesConfig = this._mConfig.modulesConfig();
        // recupération des routes de 'modules'
        const routesModules = this.getRoutesModules();

        // récupération de la route 'page not found pour la remettre à la fin après l'ajout des routes
        const pageNotFoundRoute = routesModules.splice(
          routesModules.findIndex((route) => route.path == '**'),
          1
        )[0];

        // ajout des routes (en fonction de la config des modules)
        this.addModulesRoutes(routesModules, modulesConfig);

        // on replace la route 'page not found' à la fin
        routesModules.push(pageNotFoundRoute);

        // mise à jour effective des routes du router
        this._router.resetConfig(this._router.config);

        // retour et subjects
        this.routesLoaded = true;
        this.routesLoadedSubject.next(true);
        this.routesLoadedSubject.complete();

        return of(true);
      })
    );
  }

  /**
   * fonction qui lit la config des modules et ajoute les routes à la config du router
   */
  addModulesRoutes(routesModules, modulesConfig) {
    for (const [moduleCode, moduleConfig] of Object.entries(modulesConfig)) {
      for (const [pageCode, pageConfig] of Object.entries(moduleConfig['pages'] || {})) {
        const pagePath = !!pageConfig['url']
          ? `${moduleCode.toLowerCase()}/${pageConfig['url']}`
          : `${moduleCode.toLowerCase()}`;
        routesModules.push({
          path: pagePath,
          component: PageComponent,
          data: {
            moduleCode: moduleCode,
            pageCode,
          },
        });
      }
    }
  }

  /**
   *
   * fonction qui récupère les routes de 'modules'
   */
  getRoutesModules() {
    const pathTest = this._mConfig.MODULE_URL.replace('/', '');
    return this._router.config
      .find((config) => !!config.children)
      .children.find((config) => config.path == pathTest)['_loadedRoutes'];
  }

  reloadPage() {
    this.redirect(this._router.url);
  }

  /**
   * patch pour pouvoir rediriger sur la meme url
   */
  redirect(url) {
    if (url[0] == '#') {
      url = url.substring(1);
    }
    this._router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
      this._router.navigateByUrl(url);
    });
  }

  modulePageUrl(moduleCode, pageCode, params, query = true) {
    const moduleConfig = this._mConfig.moduleConfig(moduleCode);
    const pageConfig = moduleConfig.pages[pageCode];
    if (!pageConfig) {
      this._commonService.regularToaster(
        'error',
        `Il n'a pas de route définie pour la page ${pageCode} pour le module ${moduleCode}`
      );
      return;
    }
    var url = utils.copy(pageConfig.url);

    var queryParams: Array<string> = [];
    // route params
    for (const [key, value] of Object.entries(params || {})) {
      if (pageConfig.url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, value);
      } else if (![null, undefined].includes(value as any) && query) {
        queryParams.push(`${key}=${value}`);
      }
    }

    if (queryParams) {
      url += `?${queryParams.join('&')}`;
    }

    return `${this._mConfig.MODULE_URL}/${moduleConfig.code.toLowerCase()}/${url}`;
  }

  navigateToPage(moduleCode, pageCode, params, query = true) {
    const url = this.modulePageUrl(moduleCode, pageCode, params, query);
    // verification de l'url
    // est ce que les variables avec ':' sont résolues
    // est ce que l'on a un parmètre à null
    if (['null', ':'].some((c) => url?.includes(c))) {
      console.error(`url non valide: ${url}`);
      return;
    }

    if (!url) {
      return;
    }
    // patch sinon navigateByUrl met des plombes...
    const baseUrl = window.location.href.replace(this._router.url, '');
    setTimeout(() => {
      window.location.href = baseUrl + url;
    });
  }
}
