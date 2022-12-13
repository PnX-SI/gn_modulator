import { Injectable, Injector } from '@angular/core';
import { AuthService, User } from '@geonature/components/auth/auth.service';

@Injectable()
export class ModulesContextService {
  _auth: AuthService;
  _module_code;
  _page_code;
  _object_code;
  _current_user;
  _params;

  constructor(private _injector: Injector) {
    this._auth = this._injector.get(AuthService);
  }

  initContext({
    _module_code = null,
    _object_code = null,
    _page_code = null,
    _params = null,
  } = {}) {
    this._module_code = _module_code || 'MODULES';
    this._page_code = _page_code;
    this._page_code = _page_code;
    this._params = _params || {};
    this._object_code = _object_code;
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
      _module_code: this.getContextElem('_module_code', { data, layout, context }),
      _page_code: this.getContextElem('_page_code', { data, layout, context }),
      _object_code: this.getContextElem('_object_code', { data, layout, context }),
      _params: this.getContextElem('_params', { data, layout, context }),
      _current_user: this._current_user,
    };
  }
}
