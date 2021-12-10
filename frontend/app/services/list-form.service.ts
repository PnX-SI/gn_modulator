import { Injectable } from "@angular/core";


import { of } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import { ModulesConfigService } from "./config.service";
import { ModulesDataService } from "./data.service"

@Injectable()
export class ListFormService {

  constructor(
    private _requestService: ModulesRequestService,
    private _mConfig: ModulesConfigService,
  ) {}

  init() {
  }

  /**
   * entrees
   *  - options
   *  - value
   *
   * sorties
   *  - model
   *  - selectList
   *
   */
  initListForm(options, value) {
    var model;
    return of(true)
      .pipe(

        // init config
        mergeMap(() => { return this.initConfig(options)}),

        // form to model
        mergeMap(() => { return this.formToModel(options, value)}),

        // get selectList
        mergeMap((_model) => { model = _model; return this.getSelectList(options, model)}),

        // return selectList Model
        mergeMap((selectList) => { return of({selectList, model});})

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

    // gestion des nomenclatures pour simplifier la config du layout
    if (options.nomenclature_type) {
      options.schema_name = options.schema_name || 'schemas.utils.nomenclature';
      options.params = options.params || {}
      options.params.filters = options.params.filters || [];
      options.params.filters.push({field: 'type.mnemonique', type: '=', value: options.nomenclature_type})
      options.useCache = true;
    }

    if (options.schema_name) {
      return this._mConfig.loadConfig(options.schema_name)
        .pipe(
          mergeMap(() => {
            options.api = options.api || this._mConfig.schemaConfig(options.schema_name).utils.urls.rest;
            options.value_field_name =  options.value_field_name ||this._mConfig.schemaConfig(options.schema_name).utils.value_field_name;
            options.label_field_name = options.label_field_name || this._mConfig.schemaConfig(options.schema_name).utils.label_field_name;
            // size
            return of(true)
          }),
        )
    }

    return of(true)
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
    if(options.items) {
      return of(options.items);
    }

    if(options.api) {
      const params = {
        /**
         * sans tous les champs, l'option return Object passe mal
         * => error sur les champs manquants?
         **/
        fields: options.return_object ? null : [options.value_field_name, options.label_field_name],
        ...options.params
      };
      params.filters = (params.filters || []);
      if (options.search || true) {
        params.filters.push(
          { field: options.label_field_name, type: 'ilike', value: options.search }
        )
      };

      const values = options.multiple
        ? value
        : value
          ? [value]
          : [];

      // filtre pour ne pas récupérer les valeurs qui sont déjà dans value
      if (values.length) {
        params.filters.push(
          ...[
            '!',
            {
              field: options.value_field_name,
              type: 'in',
              value: values.map(v => v[options.value_field_name])
            }
          ]
        )
      }

      return this._requestService.request('get', options.api, { params, useCache: options.useCache })
        .pipe(
          mergeMap( (res: any) => {
            return of([
              ...values,
              ...res.data
            ])
          })
        );
    }
  }

    /**
   * Observable
   */
     formToModel(options, value) {
      let model;

      /**
       * Cas simple, on a déjà un objet
       */
      if (options.return_object) {
        model = options.multiple
        ? (value || [])
        : value

      return of(model);

      /**
       * Cas moins simple, on a seulement les id, il faut requêter les valeurs
       */
      } else {

        /** on passe en array */
        const values = value
          ? options.multiple
            ? value
            : [value]
          : []
        ;

        const filters = values.length
          ? [
              {
                field: options.value_field_name,
                type: 'in',
                value: values
              }
            ]
          : [];

        return ( values.length
          ? this._requestService.request(
            'get',
            options.api,
            {
              params: {
                filters
              }
            }
          )
          : of([])
        ).pipe(
          mergeMap((res: any) => {
            let data = values.map( v =>
              res.data.find( d =>
                d[options.value_field_name] == v
              )
            );

            data = options.multiple
                ? data
                : data[0]

            return of(data);
          })
        );
      }
    }

  modelToForm(options, model) {

    return  options.return_object
      ? model
      : options.multiple
        ? model.map( m => m[options.value_field_name])
        : model && model[options.value_field_name]
    ;
  }
}