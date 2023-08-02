import { Injectable } from '@angular/core';

import { ModuleService as GnModuleService } from '@geonature/services/module.service';

import { of, forkJoin } from '@librairies/rxjs';
import { mergeMap } from '@librairies/rxjs/operators';
import { ModulesRequestService } from './request.service';
import { ConfigService as GNConfigService } from '@geonature/services/config.service';
import utils from '../utils';
@Injectable()
export class ModulesConfigService {
  private _config: any = {
    schemas: {},
    modules: {},
    layouts: {},
  };

  constructor(
    private _gnModuleService: GnModuleService,
    private _mRequest: ModulesRequestService,
    private AppConfig: GNConfigService,
  ) {}

  /** Configuration */

  MODULE_CODE = 'MODULATOR';
  MODULE_URL = 'modulator';

  init() {
    return forkJoin({
      config: this.getModulesConfig(),
      layout: this.getLayouts(),
      schema: this.getSchemas(),
    }).pipe(
      mergeMap(() => {
        // on attibue les droits aux module (depuis le ModuleService de GN)
        this.setModuleCruved(this._config.modules);
        return of(true);
      }),
    );
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
      }),
    );
  }

  setModuleCruved(modules) {
    for (const [moduleCode, moduleConfig] of Object.entries(modules)) {
      const moduleGN = this._gnModuleService.getModule(moduleCode);
      if (!moduleGN) {
        continue;
      }
      (moduleConfig as any)['cruved'] = this._gnModuleService.getModule(moduleCode)['cruved'];
    }
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
    const pageConfig =
      this.moduleConfig(moduleCode).pages && this.moduleConfig(moduleCode).pages[pageCode];
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

  schema(schemaCode) {
    return this._config['schemas'][schemaCode];
  }

  getSchemas() {
    return Object.keys(this._config.schemas).length
      ? of(this._config.schemas)
      : this._mRequest.request('get', `${this.backendModuleUrl()}/schemas/?as_dict=true`).pipe(
          mergeMap((schemas) => {
            this._config.schemas = schemas;
            return of(this._config.schemas);
          }),
        );
  }

  getLayouts() {
    return Object.keys(this._config.layouts).length
      ? of(this._config.layouts)
      : this._mRequest.request('get', `${this.backendModuleUrl()}/layouts/?as_dict=true`).pipe(
          mergeMap((data) => {
            this._config.layouts = data;
            return of(true);
          }),
        );
  }

  backendUrl() {
    return `${this.AppConfig.API_ENDPOINT}`;
  }

  urlApplication() {
    return `${this.AppConfig.URL_APPLICATION}`;
  }

  appConfig() {
    return this.AppConfig;
  }

  moduleURL() {
    return this.AppConfig[this.MODULE_CODE].MODULE_URL;
  }

  /** Backend Module Url */
  backendModuleUrl() {
    return `${this.AppConfig.API_ENDPOINT}${this.moduleURL()}`;
  }

  moduleImg(moduleCode) {
    const moduleImg = `${this.backendUrl()}/${
      this.AppConfig.MEDIA_URL
    }/modulator/config/${moduleCode.toLowerCase()}/assets/module.jpg`;
    return moduleImg;
  }

  exportUrl(moduleCode, objectCode, exportCode, options: any = {}) {
    const url = this._mRequest.url(
      `${this.backendUrl()}/modulator/exports/${moduleCode.toLowerCase()}/${objectCode}/${exportCode}`,
      {
        prefilters: options.prefilters,
        filters: options.filters,
      },
    );
    return url;
  }

  objectUrl(moduleCode, objectCode, value = '', urlSuffix = '') {
    return `${this.backendUrl()}/modulator/${urlSuffix || 'rest'}/${moduleCode}/${objectCode}/${
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
