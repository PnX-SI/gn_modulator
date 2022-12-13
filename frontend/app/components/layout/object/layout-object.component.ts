import { Component, OnInit, Injector } from '@angular/core';
import { ModulesConfigService } from '../../../services/config.service';
import { ModulesObjectService } from '../../../services/object.service';
import { ModulesDataService } from '../../../services/data.service';
import { ModulesPageService } from '../../../services/page.service';
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
  objectContext;
  processedLayout; // layout pour form / details / etc..

  /** modules services */
  _mConfig: ModulesConfigService;
  _mObject: ModulesObjectService;
  _mData: ModulesDataService;
  _mRoute: ModulesRouteService;
  _mPage: ModulesPageService;

  /** subscription pour les informations sur les objects */

  constructor(_injector: Injector) {
    super(_injector);
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mData = this._injector.get(ModulesDataService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._mRoute = this._injector.get(ModulesRouteService);
    this._mPage = this._injector.get(ModulesPageService);
    this._name = 'layout-object';
    this.bPostComputeLayout = true;
  }

  log(...args) {
    console.log(
      this._name,
      this.layout && this.layout.type,
      this.layout.diplay,
      this.data._object_code,
      this.data.schema_code,
      this._id,
      ...args
    );
  }

  postComputeLayout(dataChanged: any, layoutChanged: any): void {
    if (!utils.fastDeepEqual(this.data.value, this.dataSave?.value)) {
      this.processValue(this.data.value);
    }
    if (!utils.fastDeepEqual(this.data.filters, this.dataSave?.filters)) {
      this.processFilters();
    }
    if (!utils.fastDeepEqual(this.data.prefilters, this.dataSave?.prefilters)) {
      this.processPreFilters();
    }
  }

  postProcessLayout() {
    return this.processObject();
  }

  postProcessContext(): void {
    if (this._name == 'layout-object' && this.layout.key) {
      utils.addKey(this.context.data_keys, this.layout.key);
    }

    this.objectContext = {};
    this.objectContext._module_code = this.context._module_code;
    this.objectContext._object_code = this.context._object_code;
    this.objectContext.debug = this.context.debug;
    this.objectContext.data_keys = [];
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
      }
    );
  }

  processTotalFiltered(response) {
    if (![null, undefined].includes(response.total)) {
      this.data.total = response.total;
      this.data.filtered = response.filtered;
      this._mLayout.reComputeLayout('totalfilter');
    }
  }

  /** Traitement de la configuration */
  processConfig() {
    // cas du formulaire
    if (this.computedLayout.display == 'form') {
      this.processedLayout = this._mObject.processFormLayout(
        this._mPage.moduleCode,
        this.objectCode()
      );
    }

    // cas des details ou propriété
    if (this.computedLayout.display == 'properties') {
      this.processedLayout = this._mObject.processPropertiesLayout(
        this._mPage.moduleCode,
        this.objectCode()
      );
    }

    // export ??
    if (this.computedLayout.display == 'export') {
      this.processedLayout = {
        type: 'button',
        title: 'export',
        icon: 'file_download',
        href: this._mConfig.exportUrl(
          this._mPage.moduleCode,
          this.objectCode(),
          this.computedLayout.export_code,
          this.data
        ),
        description: 'Exporter les données',
      };
    }
  }

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
    for (const [defaultKey, defaultValue] of Object.entries(this.data.defaults || {})) {
      if (!((defaultValue as any).length && (defaultValue as any)[0] == ':')) {
        data[defaultKey] = defaultValue;
      }
    }
  }

  // récupération des données
  // peut être redefini
  getData(): Observable<any> {
    if (['form', 'properties'].includes(this.computedLayout.display) && this.getDataValue()) {
      return this.getOneRow();
    }
    return of({});
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

    const fields = this._mObject.getFields(
      this.moduleCode(),
      this.objectCode(),
      this.processedLayout
    );

    return this._mData.getOne(this.moduleCode(), this.objectCode(), value, {
      fields,
    });
  }

  // process des actions
  // TODO à clarifier avec page.element ??
  processAction(event) {
    if (['submit', 'cancel', 'edit', 'details', 'create', 'delete'].includes(event.action)) {
      this._mPage.processAction({
        action: event.action,
        objectCode: this.objectCode(),
        value: event.data[this.pkFieldName()],
        data: event.data,
        layout: this.processedLayout,
      });
    }
  }

  // champ de clé primaire
  pkFieldName() {
    return this._mConfig.pkFieldName(this.moduleCode(), this.objectCode());
  }

  // champ pour le label
  labelFieldName() {
    return this._mConfig.labelFieldName(this.moduleCode(), this.objectCode());
  }

  setObject(data) {
    let change = false;
    for (const [key, value] of Object.entries(data)) {
      if (!utils.fastDeepEqual(this.data[key], value)) {
        change = true;
        this.data[key] = value;
      }
    }
    // s'il y a eu un changement on recalcule les layout
    if (change) {
      this._mLayout.reComputeLayout('set data object');
      // setTimeout(() => {
      // this._mLayout.reComputeHeight("set data object");
      // });
    }
  }

  // valeur associée à l'id de l'object
  getDataValue() {
    return this.data.value;
  }

  // filtres associés à l'object
  getDataFilters() {
    return this.data.filters;
  }

  // prefiltres associés à l'object
  getDataPreFilters() {
    return this.data.prefilters;
  }

  // Quand une nouvelle valeur est définie
  processValue(value) {
    if (['form', 'properties'].includes(this.computedLayout.display)) {
      return this.postProcessLayout();
    }
  }

  // quand un nouveau filtre est défini
  processFilters() {}

  // quand un nouveau prefiltre est défini
  processPreFilters() {}
}
