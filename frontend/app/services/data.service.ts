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
  dataRequest(groupName, objectName, method, options: any) {
    return this._config
      .loadConfig(groupName, objectName)
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

  getList(groupName, objectName, params = {}) {
    return this.dataRequest(
      groupName,
      objectName,
      'get',
      {
        params: {params}
      }
    );
  }


  getOne(groupName, objectName, value, fieldName=null) {
    return this.dataRequest(
      groupName,
      objectName,
      'get',
      {
        value,
        params: { fieldName }
      }
    );
  }

  post(groupName, objectName, data) {
    return this.dataRequest(
      groupName,
      objectName,
      'post',
      {
        data
      }
    );
  }

  patch(groupName, objectName, value, data, fieldName=null) {
    return this.dataRequest(
      groupName,
      objectName,
      'patch',
      {
        value,
        params: { fieldName },
        data
      }
    );
  };

  delete(groupName, objectName, value, fieldName=null) {
    return this.dataRequest(
      groupName,
      objectName,
      'delete',
      {
        value,
        params: { fieldName }
      }
    );
 
  };
}