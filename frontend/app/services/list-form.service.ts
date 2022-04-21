import { Injectable } from "@angular/core";

import { of, Observable } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import { ModulesConfigService } from "./config.service";
import { ModulesDataService } from "./data.service";
import utils from "./../utils";
@Injectable()
export class ListFormService {
  /**
   * pour test si une url est absolue ou relative ?
   * depuis https://stackoverflow.com/questions/10687099/how-to-test-if-a-url-string-is-absolute-or-relative
   */

  regexpUrlAbsolute = new RegExp("^(?:[a-z]+:)?//", "i");

  constructor(
    private _requestService: ModulesRequestService,
    private _mConfig: ModulesConfigService
  ) {}

  init() {}

  initListForm(options, control) {
    return this.initConfig(options).pipe(
      mergeMap(() => {
        return this.getSelectList(options, control.value);
      })
    );
  }

  /**
   * Si schema_name est défini dans les options
   *
   * récupération de la config du schéma pour
   *  - api
   *  - valueFieldName
   *  - labelFieldName
   */
  initConfig(options) {
    return this.processSchemaConfig(options).pipe(
      mergeMap(() => {
        options.label_field_name = options.label_field_name || "label";
        options.value_field_name = options.value_field_name || "value";
        return of(true);
      })
    );
  }

  /**
   * ajoute les éléments par défaut pour un schéma donné
   * api, value_field_name, label_field_name, title_field_name, etc....
   */
  processSchemaConfig(options) {
    /** patch
     * - nomenclature_type
     * - area_type
     **/
    let schemaFilters = [];
    if (options.nomenclature_type) {
      options.schema_name = "ref_nom.nomenclature";
      schemaFilters.push({
        field: "nomenclature_type.mnemonique",
        type: "=",
        value: options.nomenclature_type,
      });
      options.cache = true;
    }
    if (options.area_type) {
      options.schema_name = "ref_geo.area";
      schemaFilters.push({
        field: "area_type.type_code",
        type: "=",
        value: options.area_type,
      });
    }

    if (!options.schema_name) {
      return of(true);
    }
    return this._mConfig.loadConfig(options.schema_name).pipe(
      mergeMap(() => {
        options.api =
          options.api ||
          this._mConfig.schemaConfig(options.schema_name).utils.urls.rest;
        options.value_field_name =
          options.value_field_name ||
          this._mConfig.schemaConfig(options.schema_name).utils
            .value_field_name;
        options.label_field_name =
          options.label_field_name ||
          this._mConfig.schemaConfig(options.schema_name).utils
            .label_field_name;
        options.title_field_name =
          options.title_field_name ||
          this._mConfig.schemaConfig(options.schema_name).utils
            .title_field_name;
        // size ??
        options.size = options.cache ? null : options.size || 10;
        options.items_path = "data";
        options.filters = [...(options.filters || []), ...schemaFilters];
        return of(true);
      })
    );
  }

  /**
   *  getSelectList(options, value)
   *
   * recupère une liste depuis options
   *
   * si options.api est defini
   * - get api
   * - params
   *  - filtres : [
   *    // recherche
   *    - { field: options.label_field_name, type: 'ilike', value: options.search}
   *    // ne pas redemander les valeurs selectionées
   *    - '!', { field: options.label_field_name, type: 'ilike', value: options.search}
   *  ]
   *
   * TODO process all cases
   *
   */
  getSelectList(options, value) {
    if (options.items) {
      /**  Si item est une liste on */
      return of({
        items: this.processItems(options, options.items),
        nbItems: options.items.length,
      });
    }
    if (options.api) {
      return this.getItemsFromApi(options, value);
    }
    return of([]);
  }

  url(api) {
    return this.regexpUrlAbsolute.test(api)
      ? api
      : `${this._mConfig.backendUrl()}/${api}`;
  }

  /**
   * getItemsFromApi
   */
  getItemsFromApi(options, value): Observable<any> {
    const params = options.params || {};
    if (options.schema_name) {
      params.filters = utils.copy(options.filters);
      params.fields = utils.removeDoublons([options.value_field_name, options.title_field_name, options.label_field_name].filter(e => !!e))
      if(options.reload_on_search && options.search) {

        params.filters.push({
          field: options.label_field_name,
          type: "ilike",
          value: options.search
        });
      }
    }

    // size
    params.size = options.reload_on_search
      ? options.size || 10
      : 0
    ;

    return this._requestService
      .request("get", this.url(options.api), { params, cache: options.cache })
      .pipe(
        mergeMap((res) => {
          const items = this.processItems(
            options,
            options.items_path ? res[options.items_path] : res
          );
          return of({ items, nbItems: items.length });
        })
      );
  }
  /** si on a une liste de valeur simple, on renvoie une liste de dictionnaires
   * {
   *    <options.value_field_name>: item,
   *    <options.label_field_name>: item
   * }
   */
  processItems(options, items) {
    return items.map((item) => {
      if (utils.isObject(item)) {
        return item;
      }
      let d = {};
      d[options.label_field_name] = d[options.value_field_name] = item;
      return d;
    });
  }
}
