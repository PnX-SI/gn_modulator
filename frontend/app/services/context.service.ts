import { Injectable, Injector } from '@angular/core';
import { AuthService, User } from '@geonature/components/auth/auth.service';

@Injectable()
export class ModulesContextService {
  _auth: AuthService;
  module_code;
  page_code;
  current_user;
  params;

  constructor(private _injector: Injector) {
    this._auth = this._injector.get(AuthService);
  }

  initContext({ module_code, page_code, params }) {
    this.module_code = module_code || 'MODULES';
    this.params = params || {};
    this.current_user = this._auth.getCurrentUser();
    this.page_code = page_code;
  }

  getContextElem(elemKey, { data, layout, context }) {
    return (
      (layout && layout[elemKey]) ||
      (data && data[elemKey]) ||
      (context && context[elemKey]) ||
      this[elemKey]
    );
  }

  // pour les breadcrumbs
  getContext({ data, layout, context }) {
    return {
      module_code: this.getContextElem('module_code', { data, layout, context }),
      page_code: this.getContextElem('page_code', { data, layout, context }),
      object_code: this.getContextElem('object_code', { data, layout, context }),
      params: this.getContextElem('params', { data, layout, context }),
      current_user: this.current_user,
    };
  }
}
