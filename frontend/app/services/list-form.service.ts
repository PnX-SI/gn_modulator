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

  /** Initialisation du composant de liste */
  initListForm(options, control) {
    // initialisation de la configuration
    return this.initConfig(options).pipe(
      mergeMap(() => {
        // demande de la liste
        // - config
        // - api
        //    - (toutes la liste / une partie)
        return this.getSelectList(options, control.value);
      }),
      mergeMap((liste) => {
        // gestion des valeurs par defaut
        return this.processDefault(options, control, liste);
      }),
      mergeMap((liste) => {
        this.processListeLengthisOne(options, control, liste);
        return of(liste);
      })
    );
  }

  processListeLengthisOne(options, control, liste) {
    // si
    // - la valeur est requise
    // - la taille de la liste est 1
    // - il n'y a pas de valeur
    if (
      !(
        options.required &&
        liste.items.length == 1 &&
        [null, undefined].includes(control.value)
      )
    ) {
      return;
    }

    // cas ou la liste n'a qu'une seule valeur -> par default on la choise
    // seuelement si une valeur est requise (options.required = true)
    if (options.required && liste.items.length == 1) {
      const value = liste.items[0];
      const controlValue = options.return_object
        ? value
        : value[options.value_field_name];
      control.patchValue(controlValue);
    }
  }

  /**
   * gestion des valeurs par defaut
   *  TODO traiter reload on search
   *
   */
  processDefault(options, control, liste) {
    // si pas de defaut, on ne fait rien

    // si on a déjà une valeur => retour
    if (![null, undefined].includes(control.value)) {
      return of(liste);
    }

    if (!options.default) {
      return of(liste);
    }

    // recherche de la valeur dans la liste
    // recherce de la valeur par api et ajout dans la liste
    const value = liste.items.find((item) =>
      Object.entries(options.default).every(
        ([key, value]) => item[key] == value
      )
    );
    if (!value) {
      // message, erreur ?
      console.error(
        `Pas de valeur trouvée pour ${JSON.stringify(options.default)}`
      );
      return of(liste);
    }
    const controlValue = options.return_object
      ? value
      : value[options.value_field_name];
    control.patchValue(controlValue);

    return of(liste);
  }

  /**
   * Si object_name est défini dans les options
   *
   * récupération de la config du schéma pour
   *  - api
   *  - valueFieldName
   *  - labelFieldName
   */
  initConfig(options) {
    return this.processObjectConfig(options).pipe(
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
  processObjectConfig(options) {
    /** patch
     * - nomenclature_type
     * - area_type
     **/
    let schemaFilters: Array<any> = [];
    if (options.nomenclature_type) {
      options.object_name = "ref_nom.nomenclature";
      schemaFilters.push(
        `nomenclature_type.mnemonique_=_${options.nomenclature_type}`
      );
      options.cache = true;
    }
    if (options.area_type) {
      options.object_name = "ref_geo.area";
      schemaFilters.push(`area_type.type_code_=_${options.area_type}`);
    }

    if (!options.object_name) {
      return of(true);
    }

    const moduleCode = options.module_code || "MODULES";

    const objectConfig = this._mConfig.objectConfig(
      moduleCode,
      options.object_name
    );
    const objectUrl = this._mConfig.objectUrl(moduleCode, options.object_name);
    options.api = options.api || objectUrl;
    options.value_field_name =
      options.value_field_name || objectConfig.utils.value_field_name;
    options.label_field_name =
      options.label_field_name || objectConfig.utils.label_field_name;
    options.title_field_name =
      options.title_field_name || objectConfig.utils.title_field_name;
    options.page_size = options.cache ? null : options.page_size || 10;
    options.items_path = "data";
    options.schema_filters = schemaFilters;
    return of(true);
  }

  /**
   *  getSelectList(options, value)
   *
   * recupère une liste depuis options
   *
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
    // TODO test si cela ne vient pas d'être fait ?
    const params = options.params || {};
    params.filters = options.filters || "";
    if (options.object_name) {
      params.filters = [params.filters, options.schema_filters || []]
        .flat()
        .filter((f) => !!f);
      params.sort = params.sort || options.sort;

      if (options.reload_on_search && options.search) {
        params.filters.push(`${options.label_field_name}_~_${options.search}`);
      }
    }

    params.filters = utils.processFilterArray(params.filters);

    params.fields = utils
      .removeDoublons(
        [
          options.value_field_name,
          options.title_field_name,
          options.label_field_name,
          ...(options.additional_fields || []),
        ].filter((e) => !!e)
      )
      .join(",");

    params.page_size = options.reload_on_search ? options.page_size || 10 : 0;
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
   *    <options.label_field_name>: item,
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
