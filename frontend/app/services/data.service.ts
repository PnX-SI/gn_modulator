import { Injectable } from "@angular/core";

import { Observable } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesConfigService } from "./config.service";
import { ModulesRequestService } from "./request.service";

@Injectable()
export class ModulesDataService {

  constructor(
    private _requestService: ModulesRequestService,
    private _mConfig: ModulesConfigService
  ) {}

  init() {
  }

  /**
   * On souhaite s'assurer que la config est bien chargée
   * pour l'élément demandé
   */
  dataRequest(schemaName, method, routeName, options: any): Observable<any> {
    return this._mConfig
      .loadConfig(schemaName)
      .pipe(
        mergeMap((schemaConfig) => {
          const url = `${this._mConfig.schemaConfig(schemaName).utils.urls[routeName]}${options.value || ''}`;
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
      'rest',
      {
        params
      }
    );
  }


  getOne(schemaName, value, params = {}) {
    return this.dataRequest(
      schemaName,
      'get',
      'rest',
      {
        value,
        params
      }
    );
  }

  post(schemaName, data, params = {}) {
    return this.dataRequest(
      schemaName,
      'post',
      'rest',
      {
        params,
        data
      }
    );
  }

  patch(schemaName, value, data, params = {}) {
    return this.dataRequest(
      schemaName,
      'patch',
      'rest',
      {
        value,
        params,
        data
      }
    );
  };

  delete(schemaName, value, params = {}) {
    return this.dataRequest(
      schemaName,
      'delete',
      'rest',
      {
        value,
        params
      }
    );
  };

  getPageNumber(schemaName, value, params) {
    return this.dataRequest(
      schemaName,
      'get',
      'page_number',
      {
        value,
        params
      }
    );
  }

  export(moduleCode, exportCode) {
    return this._requestService.request(
      'get',
      `${this._mConfig.backendModuleUrl()}/${moduleCode}/export/${exportCode}`
    );
  }
}