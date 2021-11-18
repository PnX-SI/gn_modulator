import { Injectable } from "@angular/core";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of, Observable } from "@librairies/rxjs";
import { mergeMap, catchError } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import { CommonService } from "@geonature_common/service/common.service";

@Injectable()
export class ModulesConfigService {
  private _config;

  constructor(
    private _requestService: ModulesRequestService,
    private _commonService: CommonService
  ) {}

  /** Configuration */

  init() {
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
  loadConfig(schemaName, forceLoad=false) {

    // 1 - attempts to get config from cache (this._config)

    const schemaConfig = this._config
        && this._config[schemaName]

    //   - if forceLoad is True : fetch config
    if(schemaConfig && !forceLoad) {
        return of(schemaConfig);
    }

    // 2 - Fetch config from backend

    const urlConfig =`${this.backendModuleUrl()}/${schemaName}/config/`

    /**
     * Fetch schemaConfig and store in _config[schemaName]
     */
    return this._requestService.request('get', urlConfig).pipe(
      mergeMap(
        (schemaConfig) => {
          this._config = this._config || {};
          this._config[schemaName] = schemaConfig;
        return of(schemaConfig);
      }),
      catchError( (error:any) => {
        console.log('config error', error)
        this._commonService.regularToaster(
          "error",
          error
        );
        return Observable.throw(error)
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
    return this._config
        && this._config[schemaName]
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

  /** Frontend Module Monitoring Url */
  frontendModuleMonitoringUrl() {
    return ModuleConfig.MODULE_URL;
  }

  moduleMonitoringCode() {
    return ModuleConfig.MODULE_CODE;
  }

}