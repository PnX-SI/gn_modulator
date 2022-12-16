import { Injectable } from '@angular/core';

import { AppConfig } from '@geonature_config/app.config';
import { ModuleConfig } from '../module.config';

import { of, forkJoin } from '@librairies/rxjs';
import { mergeMap } from '@librairies/rxjs/operators';
import { ModulesRequestService } from './request.service';
import utils from '../utils';
@Injectable()
export class ModulesConfigService {
  private _config: any = {
    schemas: {},
    modules: {},
    layouts: {},
  };

  constructor(private _mRequest: ModulesRequestService) {}

  /** Configuration */

  init() {
    return forkJoin({
      config: this.getModulesConfig(),
      layout: this.getLayouts(),
    });
  }

  getModulesConfig() {
    const modulesConfig = utils.getAttr(this._config, 'modules');

    if (Object.keys(this._config.modules).length) {
      return of(this._config.modules);
    }

    return this._mRequest.request('get', `${this.backendModuleUrl()}/config/`).pipe(
      mergeMap((modulesConfig) => {
        this._config.modules = modulesConfig;
        return of(this._config.modules);
      })
    );
  }

  moduleConfig(moduleCode) {
    const moduleConfig = this._config['modules'][moduleCode];
    // if (!moduleConfig) {
    // console.error(`Le module ${moduleCode} n'est pas présent`);
    // }
    return moduleConfig;
  }

  pageConfig(moduleCode, pageCode) {
    const moduleConfig = this.moduleConfig(moduleCode);
    if (!moduleConfig) {
      return;
    }
    const pageConfig = this.moduleConfig(moduleCode).pages[pageCode];
    // if (!pageConfig) {
    // console.error(`La page ${pageCode} module ${moduleCode} n'existe pas`);
    // }
    return pageConfig;
  }

  modulesConfig() {
    return this._config['modules'];
  }

  layout(layoutCode) {
    return this._config['layouts'][layoutCode];
  }

  getLayouts() {
    return Object.keys(this._config.layouts).length
      ? of(this._config.layout)
      : this._mRequest.request('get', `${this.backendModuleUrl()}/layouts/?as_dict=true`).pipe(
          mergeMap((layouts) => {
            this._config.layouts = layouts;
            return of(this._config.layout);
          })
        );
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

  exportUrl(moduleCode, objectCode, exportName, options: any = {}) {
    const url = this._mRequest.url(
      `${this.backendUrl()}/${moduleCode}/${objectCode}/exports/${exportName}`,
      {
        prefilters: options.prefilters,
        filters: options.filters,
      }
    );
    return url;
  }

  objectUrl(moduleCode, objectCode, value = '', urlSuffix = '') {
    return `${this.backendUrl()}/${moduleCode.toLowerCase()}/${objectCode}/${urlSuffix}${
      value || ''
    }`;
  }

  /** Objects */

  // objectConfig(moduleCode, objectCode) {
  //   const objectConfig = this.moduleConfig(moduleCode).objects[objectCode];
  //   if (!objectConfig) {
  //     console.error(`L'object ${objectCode} du module ${moduleCode} n'est pas présent`);
  //   }
  //   return objectConfig;
  // }

  // objectLabel(moduleCode, objectCode) {
  //   return this.objectConfig(moduleCode, objectCode).display.label;
  // }

  // objectLabels(moduleCode, objectCode) {
  //   return this.objectConfig(moduleCode, objectCode).display.labels;
  // }
}
