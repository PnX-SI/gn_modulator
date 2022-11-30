import { Injectable, Injector } from '@angular/core';
import utils from '../utils';
import { Subject } from '@librairies/rxjs';
import { ModulesConfigService } from '../services/config.service';
import { ModulesObjectService } from './object.service';
import { AuthService, User } from '@geonature/components/auth/auth.service';

@Injectable()
export class ModulesLayoutService {
  _mConfig: ModulesConfigService;
  _mObject: ModulesObjectService;
  _auth: AuthService;
  utils;

  // pour pouvoir faire passer des infos au layout
  // - par exemple sur l'utilisateur courant ou autres
  //
  // meta.user : utilisateur courrant
  // meta.utils: fonction utiles
  // meta.object : fonction sur les objects (config etc....)
  _meta: any;

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
    this._auth = this._injector.get(AuthService);
  }

  $reComputeLayout = new Subject();
  $reComputedHeight = new Subject();
  $reDrawElem = new Subject();
  $refreshData = new Subject();
  $stopActionProcessing = new Subject();
  modals = {};
  $closeModals = new Subject();

  initModal(modalName) {
    if (!this.modals[modalName]) {
      this.modals[modalName] = new Subject();
    }
  }

  /**
   * Initialisation de meta qui servira dans les champs dynamique des layouts
   * _meta est un dicitonnaire qui contient
   *
   * - current_user:  information sur l'utilisateur courrant
   * - utils: des fonction utiles
   * - object: pour l'affichage des label et ++ des objects
   */
  initMeta({ module_code = 'MODULES' } = {}) {
    this._meta = {
      module_code,
      user: {
        current: this._auth.getCurrentUser(),
      },
      utils: {
        today: utils.today, // renvoie la date du jour (defaut)
        departementsForRegion: utils.departementsForRegion, // liste des dept pour une region
        YML: utils.YML,
      },
      objects: {
        label: this.objectLabel.bind(this),
      },
    };
  }

  objectLabel(objectCode) {
    return this._mConfig.objectLabel(this._meta.module_code, objectCode);
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

  // /**
  //  * Ici on ne remplace pas layout
  //  * seulement ces éléments qui sont des fonctions
  //  */

  computeLayout({ layout, data, globalData, formGroup }) {
    if (utils.isObject(layout)) {
      const computedLayout = {};
      for (const [key, value] of Object.entries(layout)) {
        computedLayout[key] = this.isStrFunction(value)
          ? this.evalLayout({
              layout: value,
              data,
              globalData,
              formGroup,
            })
          : value;
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

    const f = new Function('data', 'globalData', 'formGroup', 'meta', strFunction);

    return f;
  }

  evalLayout({ layout, data, globalData = null, formGroup = null }) {
    if (!this._meta) {
      this.initMeta();
    }
    if (this.isStrFunction(layout) && !data) {
      return null;
    }

    if (!data) {
      return layout;
    }

    if (typeof layout == 'function') {
      return layout({ data });
    }

    if (this.isStrFunction(layout)) {
      const val = this.evalFunction(layout)(data, globalData, formGroup, this._meta);
      return val !== undefined ? val : null; // on veut eviter le undefined
    }
    return layout;
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
