import { Injectable, Injector } from '@angular/core';
import utils from '../utils';
import { Subject } from '@librairies/rxjs';
import { ModulesConfigService } from '../services/config.service';
import { ModulesRequestService } from '../services/request.service';
import { ModulesContextService } from '../services/context.service';
import { ModulesObjectService } from './object.service';

declare var curData: any;

@Injectable()
export class ModulesLayoutService {
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;
  _mObject: ModulesObjectService;

  _utils: any;

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
  }

  $reComputeLayout = new Subject();
  $reComputedHeight = new Subject();
  $reDrawElem = new Subject();
  $refreshData = new Subject();
  $stopActionProcessing = new Subject();
  modals = {};
  $closeModals = new Subject();

  elementTypes = ['integer', 'string', 'textarea', 'list_form'];

  initModal(modalName) {
    if (!this.modals[modalName]) {
      this.modals[modalName] = new Subject();
    }
  }

  initUtils() {
    this._utils = {
      today: utils.today, // renvoie la date du jour (defaut)
      departementsForRegion: utils.departementsForRegion, // liste des dept pour une region
      YML: utils.YML,
      object_label: this.utilObject('label').bind(this),
      object_labels: this.utilObject('labels').bind(this),
      object_tab_label: this.objectTabLabel.bind(this),
      class_check: this.class_check,
    };
  }

  class_check(v1, v2) {
    return utils.fastDeepEqual(v1, v2) ? 'test-layout-ok' : 'test-layout-error';
  }

  utilObject(fonctionType) {
    return (context) => {
      const fnConfigName = `object${utils.capitalize(fonctionType)}`;
      try {
        return this._mConfig[fnConfigName](context.module_code, context.object_code);
      } catch (e) {
        return `Pas de config trouvée pour {module_code: ${context.module_code}, object_code: ${context.object_code}}`;
      }
    };
  }

  objectTabLabel({ data, layout, context }) {
    const nbTotal = data.nb_total;
    const nbFiltered = data.nb_filtered;
    const labels = this.utilObject('labels')({ data, layout, context });
    return nbTotal
      ? `${utils.capitalize(labels)} (${nbFiltered}/${nbTotal})`
      : `${utils.capitalize(labels)}`;
  }

  openModal(modalName, data) {
    this.modals[modalName] && this.modals[modalName].next(data);
  }

  closeModals() {
    this.$closeModals.next();
  }

  getLayoutFromCode(layoutCode): any {
    return this._mConfig.layout(layoutCode);
  }

  reComputeLayout(name) {
    this.$reComputeLayout.next(true);
  }

  reComputeHeight(name) {
    this.$reComputedHeight.next(true);
  }

  reDrawElem(name) {
    this.$reDrawElem.next(true);
  }

  refreshData(objectCode) {
    this.$refreshData.next(objectCode);
  }

  stopActionProcessing(name) {
    this.$stopActionProcessing.next(true);
  }

  isStrFunction(layout) {
    return typeof layout == 'string'
      ? '__f__' == layout.substr(0, 5)
      : Array.isArray(layout) && layout.length
      ? this.isStrFunction(layout[0])
      : false;
  }

  processLayoutDefinition(layout) {
    if (this.isStrFunction(layout)) {
      return this.evalFunction(layout);
    }

    if (Array.isArray(layout)) {
      return layout.map((elem) => this.processLayoutDefinition(elem));
    }

    if (utils.isObject(layout)) {
      const processedLayout = {};
      for (const [key, value] of Object.entries(layout)) {
        processedLayout[key] = this.processLayoutDefinition(value);
      }
      return processedLayout;
    }

    return layout;
  }

  /**
   * TODO gérer les cas element ?
   */
  getLocalData({ context, data, layout }) {
    const localData = utils.getAttr(data, context.data_keys);
    return localData;
  }

  // /**
  //  * Ici on ne remplace pas layout
  //  * seulement ces éléments qui sont des fonctions
  //  */

  computeLayout({ context, data, layout }) {
    if (utils.isObject(layout)) {
      const computedLayout = {};
      for (const [key, element] of Object.entries(layout)) {
        computedLayout[key] = this.evalLayoutElement({
          element,
          layout,
          data,
          context,
        });
      }
      return computedLayout;
    }

    return layout;
  }

  evalFunction(layout) {
    let strFunction = Array.isArray(layout) ? layout.join('') : layout;
    strFunction = strFunction.substr(5);
    if (!strFunction.includes('return ') && strFunction[0] != '{') {
      strFunction = `{ return ${strFunction} }`;
    }

    strFunction = `{
    const {layout, data, globalData, formGroup, utils, context} = x;
    ${strFunction.substr(1)}
    `;

    const f = new Function('x', strFunction);
    return f;
  }

  evalLayoutElement({ element, layout, data, context }) {
    if (!this._utils) {
      this.initUtils();
    }

    if (this.isStrFunction(element) && !data) {
      return null;
    }

    if (!data) {
      return element;
    }

    if (typeof element == 'function') {
      const globalData = data;
      const localData = utils.getAttr(globalData, context.keys);
      const val = element({
        layout,
        data: localData,
        globalData,
        utils: this._utils,
        context,
      });
      return val !== undefined ? val : null; // on veut eviter le undefined
    }

    if (this.isStrFunction(element)) {
      return this.evalLayoutElement({
        element: this.evalFunction(element),
        context,
        layout,
        data,
      });
    }
    return element;
  }

  /**
   * pour traduire un layout en formDef (pour les dynamic_form)
   */
  toFormDef(layout) {
    const formDef = utils.copy(layout);
    formDef.attribut_label = formDef.attribut_label || layout.title;
    formDef.attribut_name = formDef.attribut_name || layout.key;
    return formDef;
  }
}
