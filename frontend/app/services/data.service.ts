import { Injectable } from '@angular/core';

import { Observable } from '@librairies/rxjs';
import { ModulesConfigService } from './config.service';
import { ModulesRequestService } from './request.service';
import { HttpClient } from '@angular/common/http';
import utils from '../utils';

@Injectable()
export class ModulesDataService {
  constructor(
    private _mRequest: ModulesRequestService,
    private _mConfig: ModulesConfigService,
    private _http: HttpClient
  ) {}

  init() {}

  /**
   * On souhaite s'assurer que la config est bien chargée
   * pour l'élément demandé
   */
  dataRequest(method, moduleCode, objectCode, options: any): Observable<any> {
    // on gère ici le paramètre fields
    // - si c'est une chaine de caractère => on le transforme en string
    if (Array.isArray(options?.params?.fields)) {
      options.params.fields = options.params.fields.join(',');
    }
    if (Array.isArray(options?.params?.filters)) {
      options.params.filters = utils.processFilterArray(options.params.filters);
    }
    if (Array.isArray(options?.params?.prefilters)) {
      options.params.prefilters = utils.processFilterArray(options.params.prefilters);
    }

    const url = this._mConfig.objectUrl(moduleCode, objectCode, options.value, options.urlSuffix);
    return this._mRequest.request(method, url, {
      params: options.params,
      data: options.data,
    });
  }

  getList(moduleCode, objectCode, params = {}) {
    return this.dataRequest('get', moduleCode, objectCode, {
      params,
    });
  }

  getOne(moduleCode, objectCode, value, params = {}) {
    return this.dataRequest('get', moduleCode, objectCode, {
      value,
      params,
    });
  }

  getPageNumber(moduleCode, objectCode, value, params = {}) {
    return this.dataRequest('get', moduleCode, objectCode, {
      value,
      params,
      urlSuffix: 'page_number/',
    });
  }

  post(moduleCode, objectCode, data, params = {}) {
    return this.dataRequest('post', moduleCode, objectCode, {
      params,
      data,
    });
  }

  patch(moduleCode, objectCode, value, data, params = {}) {
    return this.dataRequest('patch', moduleCode, objectCode, {
      value,
      params,
      data,
    });
  }

  delete(moduleCode, objectCode, value, params = {}) {
    return this.dataRequest('delete', moduleCode, objectCode, {
      value,
      params,
    });
  }

  getBreadcrumbs(context: any) {
    return this._mRequest.request(
      'get',
      `${this._mConfig.backendModuleUrl()}/breadcrumbs/${context.module_code}/${context.page_code}`,
      { params: context.params }
    );
  }
}
