import { Injectable } from "@angular/core";

import { HttpClient } from "@angular/common/http";

import { of } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesConfigService } from "./config.service";

@Injectable()
export class ModulesDataService {

  constructor(
      private _http: HttpClient,
      private _config: ModulesConfigService) {}

  init() {
  }

// TODO params get

  /**
   * request get one row
   * 
   * @param moduleCode 
   * @param schemaName 
   * @param value 
   * @param fieldName 
   */
  getOne(moduleCode, schemaName, value, fieldName=null) {
    const schemaConfig = this._config.schemaConfig(moduleCode, schemaName);
    const queryParams = fieldName 
        ? `?field_name=${fieldName}`
        : ''
    ;
    const url = `${schemaConfig.utils.urls.rest}${value}${queryParams}`
    return this._http.get(url)
  }

  post(moduleCode, schemaName, data) {
    const schemaConfig = this._config.schemaConfig(moduleCode, schemaName);
    const url = `${schemaConfig.utils.urls.rest}`
    return this._http.post(url, data)
  }

  patch(moduleCode, schemaName, value, data, fieldName=null) {
    const schemaConfig = this._config.schemaConfig(moduleCode, schemaName);
    const queryParams = fieldName 
        ? `?field_name=${fieldName}`
        : ''
    ;
    const url = `${schemaConfig.utils.urls.rest}${value}${queryParams}`
    return this._http.patch(url, data)
  };

  delete(moduleCode, schemaName, value, fieldName=null) {
    const schemaConfig = this._config.schemaConfig(moduleCode, schemaName);
    const queryParams = fieldName 
        ? `?field_name=${fieldName}`
        : ''
    ;
    const url = `${schemaConfig.utils.urls.rest}${value}${queryParams}`
    return this._http.delete(url)
  };
}