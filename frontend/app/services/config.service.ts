import { Injectable } from "@angular/core";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of, Observable } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";

@Injectable()
export class ModulesConfigService {
  private _config;

  constructor(private _requestService: ModulesRequestService) {}

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
 * @param groupName
 * @param objectName
 * @param forceLoad : fetch even if schemaConfig already in cache (this._config)
 * @returns schemaConfig
 */
  loadConfig(groupName, objectName, forceLoad=false) {

    // 1 - attempts to get config from cache (this._config)

    const schemaConfig = this._config
        && this._config[groupName]
        && this._config[groupName][objectName];

    //   - if forceLoad is True : fetch config
    if(schemaConfig && !forceLoad) {
        return of(schemaConfig);
    }

    // 2 - Fetch config from backend

    const urlConfig =`${this.backendModuleUrl()}/${groupName}/${objectName}/config/`

    /**
     * Fetch schemaConfig and store in _config[groupName][objectName]
     */
    return this._requestService.request('get', urlConfig).pipe(
      mergeMap((schemaConfig) => {
        this._config = this._config || {};
        this._config[groupName] = this._config[groupName] || {};
        this._config[groupName][objectName] = schemaConfig;
        return of(schemaConfig);
      })
    );
  }

  /**
   * Returns schemaConfig
   *
   * @param groupName
   * @param objectName
   * @returns
   */
  schemaConfig(groupName, objectName) {
    return this._config
        && this._config[groupName]
        && this._config[groupName][objectName];
  }

  /** Backend Url et static dir ??*/
  backendUrl() {
    return `${AppConfig.API_ENDPOINT}`;
  }

  urlApplication() {
    return `${AppConfig.URL_APPLICATION}`;
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