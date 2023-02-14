import { Injectable, Injector } from '@angular/core';
import { AuthService } from '@geonature/components/auth/auth.service';
import { ModulesObjectService } from './object.service';
import { ModulesConfigService } from './config.service';

import utils from '../utils';
@Injectable()
export class ModulesContextService {
  _auth: AuthService;
  _mObject: ModulesObjectService;
  _mConfig: ModulesConfigService;
  module_code;
  page_code;
  object_code;
  current_user;
  params;
  config;

  constructor(private _injector: Injector) {
    this._auth = this._injector.get(AuthService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._mConfig = this._injector.get(ModulesConfigService);
  }

  initContext({
    module_code = null,
    object_code = null,
    page_code = null,
    params = null,
    config = null,
  } = {}) {
    this._mObject._cacheObjectConfig = {};
    this.module_code = module_code || this._mConfig.MODULE_CODE;
    this.page_code = page_code;
    this.page_code = page_code;
    this.params = params || {};
    this.object_code = object_code;
    this.config = config;
    this.current_user = this._auth.getCurrentUser();
  }

  getContextElem(elemKey, { layout, context }) {
    return (layout && layout[elemKey]) || (context && context[elemKey]) || this[elemKey];
  }

  getContext({ layout, context }) {
    const contextOut = {
      module_code: this.getContextElem('module_code', { layout, context }),
      page_code: this.getContextElem('page_code', { layout, context }),
      object_code: this.getContextElem('object_code', { layout, context }),
      params: this.getContextElem('params', { layout, context }),
      current_user: this.current_user,
    };

    return contextOut;
  }
}
