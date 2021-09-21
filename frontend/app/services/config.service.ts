import { Injectable } from "@angular/core";

import { HttpClient } from "@angular/common/http";
import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

import { of } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";

@Injectable()
export class ModulesConfigService {
  private _config;

  constructor(private _http: HttpClient) {}

  /** Configuration */

  init() {
  }

/**
 * attempts to get config from cache (this._config) and fetch schemaConfig from backend
 * 
 * @param moduleCode 
 * @param schemaName 
 * @param forceLoad : fetch even if schemaConfig already in cache (this._config)
 * @returns schemaConfig
 */
  loadConfig(moduleCode, schemaName, forceLoad=false) {

    // 1 - attempts to get config from cache (this._config)
    
    const schemaConfig = this._config 
        && this._config[moduleCode]
        && this._config[moduleCode][schemaName];

    //   - if forceLoad is True : fetch config
    if(schemaConfig && !forceLoad) {
        return of(schemaConfig);
    }

    // 2 - Fetch config from backend
    
    const urlConfig =`${this.backendModuleUrl()}/config/${moduleCode}/${schemaName}`

    /**
     * Fetch schemaConfig and store in _config[moduleCode][schemaName] 
     */
    return this._http.get<any>(urlConfig).pipe(
      mergeMap((schemaConfig) => {
        this._config = this._config || {};
        this._config[moduleCode] = this._config[moduleCode] || {};
        this._config[moduleCode][schemaName] = schemaConfig;
        return of(schemaConfig);
      })
    );
  }

  /**
   * Returns schemaConfig
   * 
   * @param moduleCode 
   * @param schemaName 
   * @returns 
   */
  schemaConfig(moduleCode, schemaName) {
    return this._config
        && this._config[moduleCode]
        && this._config[moduleCode][schemaName];
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
    return `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}`;
  }

  /** Frontend Module Monitoring Url */
  frontendModuleMonitoringUrl() {
    return ModuleConfig.MODULE_URL;
  }

  moduleMonitoringCode() {
    return ModuleConfig.MODULE_CODE;
  }

}