import { Injectable } from "@angular/core";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of, Observable, Subject } from "@librairies/rxjs";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import { ModulesConfigService } from "./config.service";
import { Routes,  RouterModule, Router } from "@angular/router";
import { PageComponent } from "../components/page.component";


@Injectable()
export class ModulesRouteService {

  routesLoaded=false;
  routesLoadedSubject;

  constructor(
    private _router: Router,
    private _mConfig: ModulesConfigService
  ) {
    // setTimeout(()=> {
      this.initRoutes().subscribe(() =>  {})
    // });
  }

  init() {
  }


  /**
   * initialisation des routes en fonction du retour de l'api '/modules/modules_config'
   * on utilise un subject pour gérer les appels simultanés à initRoute
   */
  initRoutes() {

      if (this.routesLoaded) {
        return of(true);
      }

      if(this.routesLoadedSubject) {
        return this.routesLoadedSubject;
      }

      this.routesLoadedSubject = new Subject<boolean>();

      return this._mConfig.getModules()
      .pipe(
        mergeMap((modulesConfig) => {

          // recupération des routes de 'modules'
          const routesModules = this.getRoutesModules();

          // récupération de la route 'page not found pour la remettre à la fin après l'ajout des routes
          const pageNotFoundRoute = routesModules.splice(routesModules.findIndex(route => route.path == "**"), 1)[0]

          // ajout des routes (en fonction de la config des modules)
          this.addModulesRoutes(routesModules, modulesConfig)

          // on replace la route 'page not found' à la fin
          routesModules.push(pageNotFoundRoute)

          // mise à jour effective des routes du router
          this._router.resetConfig(this._router.config)

          // retour et subjects
          this.routesLoaded = true;
          this.routesLoadedSubject.next(true);
          this.routesLoadedSubject.complete();

          return of(true)
      })
    );
  }



  /**
   * fonction qui lit la config des modules et ajoute les routes à la config du router
   */
  addModulesRoutes(routesModules, modulesConfig) {
    for (const [moduleName, module] of Object.entries(modulesConfig)) {
      for (const [pageName, pageConfig] of Object.entries(module['pages'])) {
        const pagePath = !!pageConfig['url']
          ? `${module['code'].toLowerCase()}/${pageConfig['url']}`
          : `${module['code'].toLowerCase()}`;

          routesModules.push(
          {
            path: pagePath,
            component: PageComponent,
            data: {
              moduleName,
              pageName
            }
          })

      }
    }
  }

  /**
   *
   * fonction qui récupère les routes de 'modules'
   */
  getRoutesModules() {
    return this._router.config
    .find(config => !!config.children)
    .children.find(config => config.path == 'modules')['_loadedConfig']
    .routes;
  }

  reloadPage() {
    this.redirect(this._router.url)
  }

  /**
   * patch pour pouvoir rediriger sur la meme url
   */
  redirect(url) {
    this._router.navigateByUrl('/', {skipLocationChange: true})
    .then(() =>  {
      this._router.navigateByUrl(url)
    });
  }

  modulePageUrl(moduleName, pageName, params) {
    const moduleConfig = this._mConfig.moduleConfig(moduleName);
    const pageConfig = moduleConfig.pages[pageName];
    var url = pageConfig.url;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, value)
    }
    return `/modules/${moduleConfig.code.toLowerCase()}/${url}`
  }

  navigateToPage(moduleName, pageName, params) {
    const url = this.modulePageUrl(moduleName, pageName, params);

    // patch sinon navigateByUrl met des plombes...
    const baseUrl = window.location.href.replace(this._router.url, '')
    window.location.href = baseUrl +url;
  }
}
