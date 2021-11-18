import { Injectable } from "@angular/core";

import {  } from "@angular/common/http";

import { of } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesConfigService } from "./config.service";
import { ModulesRequestService } from "./request.service";

@Injectable()
export class ModulesDataService {

  constructor(
    private _requestService: ModulesRequestService,
    private _config: ModulesConfigService
  ) {}

  init() {
  }

  /**
   * On souhaite s'assurer que la config est bien chargée
   * pour l'élément demandé
   */
  dataRequest(schemaName, method, options: any) {
    return this._config
      .loadConfig(schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          const url = `${schemaConfig.utils.urls.rest}${options.value || ''}`
          return this._requestService.request(
            method,
            url,
            {
              params: options.params,
              data: options.data
            }
          );
        })
      );
  }

  getList(schemaName, params = {}) {
    return this.dataRequest(
      schemaName,
      'get',
      {
        params
      }
    );
  }


  getOne(schemaName, value, field_name=null, as_geojson=null) {
    return this.dataRequest(
      schemaName,
      'get',
      {
        value,
        params: { field_name, as_geojson }
      }
    );
  }

  post(schemaName, data) {
    return this.dataRequest(
      schemaName,
      'post',
      {
        data
      }
    );
  }

  patch(schemaName, value, data, field_name=null) {
    return this.dataRequest(
      schemaName,
      'patch',
      {
        value,
        params: { field_name },
        data
      }
    );
  };

  delete(schemaName, value, field_name=null) {
    return this.dataRequest(
      schemaName,
      'delete',
      {
        value,
        params: { field_name }
      }
    );

  };
}