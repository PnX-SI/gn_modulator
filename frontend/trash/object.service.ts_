import { Injectable, Injector } from "@angular/core";
import { BehaviorSubject } from "@librairies/rxjs";
import utils from "../utils";

/**
 * Service pour gérer les valeurs des objects sous forme d'observables
 * pour que les composant puisssent communiquer des valeurs sans être reliés par des input/output
 * et pouvoir réagir en cas de changement de ces valeurs
 * - value (valeur de clé primaire)
 *  - table, carte (mise en valeur de l'élément concerné)
 * - filters
 * - prefilters
 * - schema_name
 */
@Injectable()
export class ModulesObjectService {
  _objects = {};

  constructor(private _injector: Injector) {}

  resetObjects() {
    // TODO voir si on ne supprime pas tout ?
    // pour faire un coup de propre au chargement de la pagee (ou au changement de params)
    for (const [objectName, object] of Object.entries(this._objects)) {
      for (const [key, subject] of Object.entries(object as any)) {
        (subject as any).next(null);
      }
    }
  }

  /** initialise les objects à partir des paramètres de route
   * - pour assigner une valeur à partir d'un url (ex id_site )
   * - ou bien pour assigner des prefiltre (ex visites filtree par id_site)
   */

  processPageObjectParams(objectsConfig = {}, params = {}) {
    // pour tous les object de ObjectConfig
    for (const [objectName, objects] of Object.entries(objectsConfig || {})) {
      // pour tous les paramètre d'object (value, filters, prefilters)
      for (const [objectParamName, objectParamValue] of Object.entries(
        objects as any
      )) {
        // pour tous les paramètres de route
        let processedobjectParamValue = objectParamValue;
        for (const [paramKey, paramValue] of Object.entries(params)) {
          // calcul de la valeur effective (par exemple :value est remplacé par params.value)
          processedobjectParamValue = utils.replace(
            processedobjectParamValue,
            `:${paramKey}`,
            paramValue
          );
        }
        // on place la valeur dans _object[objectName][objectName] pour quelle soit accessible par la suite
        this.setObjectValue(
          objectName,
          objectParamName,
          processedobjectParamValue
        );
      }
    }
  }

  initObject(objectName) {
    if (!this._objects[objectName]) {
      this._objects[objectName] = {};
      this._objects[objectName].value = new BehaviorSubject(null);
      this._objects[objectName].schema_name = new BehaviorSubject(null);
      this._objects[objectName].filters = new BehaviorSubject(null);
      this._objects[objectName].prefilters = new BehaviorSubject(null);
    }
  }

  setObjectValue(objectName, valName, value) {
    this.initObject(objectName);
    this._objects[objectName][valName].next(value);
  }

  getObjectSubject(objectName, valName) {
    return (
      this._objects[objectName]?.[valName] && this._objects[objectName][valName]
    );
  }

  getObjectValue(objectName, valName) {
    return this.getObjectSubject(objectName, valName)?.getValue();
  }
}
