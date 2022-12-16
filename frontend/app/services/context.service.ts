import { Injectable, Injector } from '@angular/core';
import { AuthService } from '@geonature/components/auth/auth.service';
import { ModulesObjectService } from './object.service';

import utils from '../utils';
@Injectable()
export class ModulesContextService {
  _auth: AuthService;
  _mObject: ModulesObjectService;

  module_code;
  page_code;
  object_code;
  current_user;
  params;

  constructor(private _injector: Injector) {
    this._auth = this._injector.get(AuthService);
    this._mObject = this._injector.get(ModulesObjectService);
  }

  initContext({ module_code = null, object_code = null, page_code = null, params = null } = {}) {
    this._mObject._cacheObjectConfig = {};
    this.module_code = module_code || 'MODULES';
    this.page_code = page_code;
    this.page_code = page_code;
    this.params = params || {};
    this.object_code = object_code;
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
