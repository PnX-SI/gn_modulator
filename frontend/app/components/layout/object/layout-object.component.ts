import { Component, OnInit, Injector } from '@angular/core';
import { ModulesConfigService } from '../../../services/config.service';
import { ModulesObjectService } from '../../../services/object.service';
import { ModulesDataService } from '../../../services/data.service';
import { ModulesActionService } from '../../../services/action.service';
import { ModulesRouteService } from '../../../services/route.service';
import { ModulesLayoutComponent } from '../base/layout.component';
import { Observable, of } from '@librairies/rxjs';
import utils from '../../../utils';

/** Composant pour afficher des objets
 * layout
 *  - object_code: référence à object défini dans module.yml
 *  - component:
 *    - map, table: liste d'object sur une carte
 *    - properties, form: pour 1 object (d'id=value)
 */
@Component({
  selector: 'modules-layout-object',
  templateUrl: 'layout-object.component.html',
  styleUrls: ['../../base/base.scss', 'layout-object.component.scss'],
})
export class ModulesLayoutObjectComponent extends ModulesLayoutComponent implements OnInit {
  objectData; // données relative au schema, récupérées par getData
  processedLayout; // layout pour form / details / etc..

  /** modules services */
  _mConfig: ModulesConfigService;
  _mObject: ModulesObjectService;
  _mData: ModulesDataService;
  _mRoute: ModulesRouteService;
  _mAction: ModulesActionService;

  /** subscription pour les informations sur les objects */

  constructor(_injector: Injector) {
    super(_injector);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mData = this._injector.get(ModulesDataService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mAction = this._injector.get(ModulesActionService);
    this._name = 'layout-object';
    this.bPostComputeLayout = true;
  }

  postInit() {
    this._subs['reProcess'] = this._mObject.$reProcessObject.subscribe(
      ({ moduleCode, objectCode }) => {
        if (this.moduleCode() == moduleCode && this.objectCode() == objectCode) {
          this.processObject();
        }
      },
    );
  }

  postComputeLayout(dataChanged: any, layoutChanged: any, contextChanged: any): void {
    if (!utils.fastDeepEqual(this.context.value, this.contextSave?.value)) {
      this.processValue(this.context.value);
    }
    if (!utils.fastDeepEqual(this.context.filters, this.contextSave?.filters)) {
      this.processFilters();
    }
    if (!utils.fastDeepEqual(this.context.prefilters, this.contextSave?.prefilters)) {
      this.processPreFilters();
    }
  }

  postProcessLayout() {
    return this.processObject();
  }

  preProcessContext(): void {
    if (this._name == 'layout-object' && this.layout.key) {
      utils.addKey(this.context.data_keys, this.layout.key);
    }
  }

  /**
   * processObject()
   *  - loadConfig: chargement de la configuration du schema
   *  - processConfig: traitement de la configuration (layout etc..)
   *  - getData: chargement des données
   *  - processData: traitement des données
   */
  processObject(): void {
    if (this.isProcessing) {
      return;
    }
    this.isProcessing = true;

    this.processConfig();
    this.getData().subscribe(
      (response) => {
        if (response) {
          this.processTotalFiltered(response);

          // traitement des données
          this.processData(response);
        }
        // traitement terminé
        this.isProcessing = false;
      },
      (error) => {
        console.error(error);
        this.isProcessing = false;
        return of(false);
      },
    );
  }

  processTotalFiltered(response) {
    if (![null, undefined].includes(response.total)) {
      this.setObject({ nb_total: response.total, nb_filtered: response.filtered });
      this.context.nb_total = response.total;
      this.context.nb_filtered = response.filtered;
      this._mLayout.reComputeLayout('totalfilter');
    }
  }

  /** Traitement de la configuration */
  processConfig() {}

  // traitement des données
  // peut être redefini
  processData(data) {
    this.processDefaults(data);
    this.objectData = data;
  }

  // traitement des valeurs par défaut
  // dans le cas du formulaire seulement ?
  // si data.default est défini
  processDefaults(data) {
    const objectConfig = this.objectConfig();
    for (const [defaultKey, defaultValue] of Object.entries(objectConfig.defaults || {})) {
      if (!((defaultValue as any).length && (defaultValue as any)[0] == ':')) {
        data[defaultKey] = defaultValue;
      }
    }
  }

  // récupération des données
  // peut être redefini
  getData(): Observable<any> {
    if (
      !['geojson', 'table', 'filters'].includes(this.computedLayout.display) &&
      this.getDataValue()
    ) {
      return this.getOneRow();
    }
    return of({});
  }

  // renvoie la liste des clés concernées par le layout
  // sert pour l'appel aux api
  fields({ geometry = false, addDefault = false, columns = false } = {}) {
    if (!this.layout.items) {
      return this.defaultFields({ geometry });
    }

    // aout des champs manquants ?

    const fields = this._mLayout.getLayoutFields(this.layout.items, this.context, null);

    if (addDefault) {
      for (const key of this.defaultFields({ geometry })) {
        if (!fields.includes(key)) {
          fields.push(key);
        }
      }
    }

    return fields;
  }

  /** champs par defaut si non définis dans items  */
  defaultFields({ geometry = false } = {}) {
    const defaultFields = [this.pkFieldName(), this.labelFieldName(), 'scope'];
    if (this.computedLayout.display == 'geojson' && geometry) {
      defaultFields.push(this.geometryFieldName());
    }
    return defaultFields;
  }

  /**
   * getOneRow
   * Utilisé par detail et form (et autre ??)
   * pour récupérer un ligne identifiées par <id> = value
   */
  getOneRow() {
    const value = this.getDataValue();
    if (!value) {
      return of(null);
    }

    const fields = this.fields({ addDefault: true });

    return this._mData.getOne(this.moduleCode(), this.objectCode(), value, {
      fields,
    });
  }

  // process des actions
  // TODO à clarifier avec page.element ??
  processAction(event) {
    if (['submit', 'cancel', 'edit', 'details', 'create', 'delete'].includes(event.action)) {
      let isSameObject = ['object_code', 'module_code'].every(
        (k) => this.context[k] == event.context[k],
      );
      this._mAction.processAction({
        action: event.action,
        context: event.context,
        value: isSameObject && event.data[this.pkFieldName()],
        data: event.data,
        layout: event.layout,
      });
    }
  }

  // champ de clé primaire
  pkFieldName() {
    return this._mObject.pkFieldName({ context: this.context });
  }

  // champ pour le label
  labelFieldName() {
    return this._mObject.labelFieldName({ context: this.context });
  }

  geometryFieldName() {
    return this._mObject.geometryFieldName({ context: this.context });
  }

  setObject(data) {
    let change = false;

    const objectConfig = this.objectConfig();

    for (const [key, value] of Object.entries(data)) {
      if (!utils.fastDeepEqual(objectConfig[key], value)) {
        change = true;
        objectConfig[key] = value;
      }
    }
    // s'il y a eu un changement on recalcule les layout
    if (change) {
      this._mLayout.reComputeLayout('set data object');
    }
  }

  // valeur associée à l'id de l'object
  getDataValue() {
    return this.context.value;
  }

  // filtres associés à l'object
  getDataFilters() {
    return this.context.filters;
  }

  // prefiltres associés à l'object
  getDataPreFilters() {
    return this.context.prefilters;
  }

  // Quand une nouvelle valeur est définie
  processValue(value) {
    if (!['geojson', 'table'].includes(this.computedLayout.display)) {
      return this.postProcessLayout();
    }
  }

  // quand un nouveau filtre est défini
  processFilters() {}

  // quand un nouveau prefiltre est défini
  processPreFilters() {}
}
