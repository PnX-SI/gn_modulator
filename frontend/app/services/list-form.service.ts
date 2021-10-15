import { Injectable } from "@angular/core";


import { of } from "@librairies/rxjs";
import { mergeMap } from "@librairies/rxjs/operators";
import { ModulesRequestService } from "./request.service";
import { ModulesDataService } from "./data.service"

@Injectable()
export class ListFormService {

  constructor(
    private _requestService: ModulesRequestService,
  ) {}

  init() {
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
          { field: options.label_field_name, type: 'ilike', value: options.search}
        )
      };

      const values = options.multiple
        ? value
        : value
          ? [value]
          : [];

      // filtre pour ne pas récupérer les valeurs qui sont déjà dans value
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

      return this._requestService.request('get', options.api, { params: { params } })
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

        return this._requestService.request(
          'get',
          options.api,
          {
            params: {
              params: {
                filters : [
                  {
                    field: options.value_field_name,
                    type: 'in',
                    value: values
                  }
                ]
              }
            }
          }
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
        : model[options.value_field_name]
    ;
  }
}