import { Injectable } from "@angular/core";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of, Observable } from "@librairies/rxjs";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import utils from '../utils';
@Injectable()
export class ModulesConfigService {

  private _config: any = {
    schemas: {},
    modules: {}
  };

  constructor(
    private _requestService: ModulesRequestService,
  ) {
  }

  /** Configuration */

  init() {
  }

  getModules() {
    const modulesConfig = utils.getAttr(this._config, 'modules');

    if(Object.keys(this._config.modules).length) {
      return of(this._config.modules);
    }

    return this._requestService
      .request('get', `${this.backendModuleUrl()}/modules_config`)
      .pipe(
        mergeMap((modulesConfig)=> {
          this._config.modules = modulesConfig;
          return of(modulesConfig);
        })
      );
  }

  /**
   * Renvoie l'ensemble des groupes de schema
   */
  getSchemaGroups() {
    return this._requestService
      .request('get', `${this.backendModuleUrl()}/groups`)
  }


/**
 * attempts to get config from cache (this._config) and fetch schemaConfig from backend
 *
 * @param schemaName
 * @param forceLoad : fetch even if schemaConfig already in cache (this._config)
 * @returns schemaConfig
 */
  loadConfig(schemaName, forceLoad=false): Observable<any> {

    // 1 - attempts to get config from cache (this._config)

    const schemaConfig = this._config['schemas'][schemaName];
        // && this._config['schemas']
        // && this._config['schemas'][schemaName]

    //   - if forceLoad is True : fetch config
    if(schemaConfig && !forceLoad) {
        return of(schemaConfig);
    }

    // 2 - Fetch config from backend

    const urlConfig =`${this.backendModuleUrl()}/${schemaName}/config/`

    /**
     * Fetch schemaConfig and store in _config[schemaName]
     */
    return this._requestService.request('get', urlConfig, {params: {reload: true}}).pipe(
      mergeMap(
        (schemaConfig) => {
          this._config['schemas'][schemaName] = schemaConfig;
        return of(schemaConfig);
      }),
    );
  }

  /**
   * Returns schemaConfig
   *
   * @param schemaName
   * @returns
   */
  schemaConfig(schemaName) {
    return this._config['schemas'][schemaName];
  }

  moduleConfig(moduleName) {
    return this._config['modules'][moduleName];
  }



  /** Backend Url et static dir ??*/
    backendUrl() {
    return `${AppConfig.API_ENDPOINT}`;
  }

  urlApplication() {
    return `${AppConfig.URL_APPLICATION}`;
  }

  appConfig() {
    return AppConfig;
  }

  /** Backend Module Url */
  backendModuleUrl() {
    return `${AppConfig.API_ENDPOINT}${ModuleConfig.MODULE_URL}`;
  }

  assetsDirectory() {
    return this.backendUrl() + '/static/external_assets/modules';
  }

}