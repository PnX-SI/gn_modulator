import { Injectable } from "@angular/core";

import { Observable } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesConfigService } from "./config.service";
import { ModulesRequestService } from "./request.service";
import { HttpClient } from "@angular/common/http";

@Injectable()
export class ModulesDataService {
  constructor(
    private _requestService: ModulesRequestService,
    private _mConfig: ModulesConfigService,
    private _http: HttpClient
  ) {}

  init() {}

  /**
   * On souhaite s'assurer que la config est bien chargée
   * pour l'élément demandé
   */
  dataRequest(method, moduleCode, objectName, options: any): Observable<any> {
    // on gère ici le paramètre fields
    // - si c'est une chaine de caractère => on le transforme en string
    if (Array.isArray(options?.params?.fields)) {
      options.params.fields = options.params.fields.join(",");
    }
    const url = this._mConfig.objectUrl(
      moduleCode,
      objectName,
      options.value,
      options.urlSuffix,
    );
    return this._requestService.request(method, url, {
      params: options.params,
      data: options.data,
    });
  }

  getList(moduleCode, objectName, params = {}) {
    return this.dataRequest("get", moduleCode, objectName, {
      params,
    });
  }

  getOne(moduleCode, objectName, value, params = {}) {
    return this.dataRequest("get", moduleCode, objectName, {
      value,
      params,
    });
  }

  getPageNumber(moduleCode, objectName, value, params = {}) {
    return this.dataRequest("get", moduleCode, objectName, {
      value,
      params,
      urlSuffix: "page_number/",
    });
  }

  post(moduleCode, objectName, data, params = {}) {
    return this.dataRequest("post", moduleCode, objectName, {
      params,
      data,
    });
  }

  patch(moduleCode, objectName, value, data, params = {}) {
    return this.dataRequest("patch", moduleCode, objectName, {
      value,
      params,
      data,
    });
  }

  delete(moduleCode, objectName, value, params = {}) {
    return this.dataRequest("delete", moduleCode, objectName, {
      value,
      params,
    });
  }
}
