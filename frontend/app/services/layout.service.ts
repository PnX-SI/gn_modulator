import { Injectable, Injector } from '@angular/core';
import utils from '../utils';
import { Subject } from '@librairies/rxjs';
import { ModulesConfigService } from '../services/config.service';
import { ModulesRequestService } from '../services/request.service';
import { ModulesObjectService } from './object.service';

@Injectable()
export class ModulesLayoutService {
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;
  _mObject: ModulesObjectService;

  _utils: any;
  _utilsObject: any;

  _formControls = {};
  _properties = {};

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
    this._mObject = this._injector.get(ModulesObjectService);
  }

  $reComputeLayout = new Subject();
  $reComputedHeight = new Subject();
  $reDrawElem = new Subject();
  $refreshData = new Subject();
  $stopActionProcessing = new Subject();
  _modals = {};
  $closeModals = new Subject();

  getFormControl(formId) {
    return this._formControls[formId];
  }

  setFormControl(formControl, formId) {
    this._formControls[formId] = formControl;
  }

  initModal(modalName) {
    if (!this._modals[modalName]) {
      this._modals[modalName] = new Subject();
    }
  }

  openModal(modalName, data) {
    this._modals[modalName] && this._modals[modalName].next(data);
  }

  closeModals() {
    this.$closeModals.next();
  }

  initUtils() {
    this._utils = {
      today: utils.today, // renvoie la date du jour (defaut)
      departementsForRegion: utils.departementsForRegion, // liste des dept pour une region
      YML: utils.YML,
    };

    this._utilsObject = this._mObject.utilsObject();
  }

  reComputeLayout(name: any = null) {
    this.$reComputeLayout.next(true);
  }

  reComputeHeight(name: any = null) {
    this.$reComputedHeight.next(true);
  }

  reDrawElem(name: any = null) {
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
      ? '__f__' == layout.substring(0, 5)
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

  flatLayout = (layout) => {
    if (layout == null) {
      return [];
    }
    if (Array.isArray(layout)) {
      return utils
        .flatAndRemoveDoublons(layout.map((elem) => this.flatLayout(elem)))
        .filter((x) => !!x);
    }
    if (utils.isObject(layout)) {
      if (layout.code) {
        const layoutFromCode = this.getLayoutFromCode(layout.code, layout.template_params);
        return this.flatLayout(layoutFromCode.layout);
      }

      if (layout.key) {
        return [layout];
      }
      if ('items' in layout) {
        return this.flatLayout(layout.items);
      }
    }

    if (typeof layout == 'string') {
      return [layout];
    }
  };

  getLayoutFromCode(layoutCode, templateParams) {
    // message d'erreur pour indiquer que l'on a pas trouvé le layout
    let layoutFromCode = this._mConfig.layout(layoutCode);
    if (!layoutFromCode) {
      return {
        layout: {
          type: 'message',
          class: 'error',
          html: `Pas de layout trouvé pour le <i>layout_code</i> <b>${layoutCode}</b>`,
        },
      };
    }

    //
    const processedTemplateParams = {
      ...(layoutFromCode.template_defaults || {}),
      ...(templateParams || {}),
    };
    // remplacer les élements de params
    for (const [paramKey, paramValue] of Object.entries(processedTemplateParams)) {
      layoutFromCode = utils.replace(layoutFromCode, `__${paramKey.toUpperCase()}__`, paramValue);
    }

    // checker s'il ne reste pas de params ??
    const regex = /(__[A-Z_]+?__)/g;
    let unresolved = JSON.stringify(layoutFromCode).match(regex);
    if (!!unresolved) {
      return {
        layout: {
          type: 'message',
          class: 'error',
          html: `<b>${layoutCode}</b> : champ(s) non résolu(s)
          <ul><li>${utils.removeDoublons(unresolved).join('</li><li>')}</li></ul>`,
        },
      };
    }

    return layoutFromCode;
  }

  // /**
  //  * Ici on ne remplace pas layout
  //  * seulement ces éléments qui sont des fonctions
  //  */

  propertyKey(context, layout) {
    return `${context.module_code}_${context.object_code}_${context.data_keys.join('.')}.${layout}`;
  }

  computeLayout({ context, data, layout }) {
    if (typeof layout == 'string' && context.module_code && context.object_code) {
      if (this._properties[this.propertyKey(context, layout)]) {
        return this._properties[this.propertyKey(context, layout)];
      }

      let property = utils.copy(this._mObject.property(context, layout));

      // patch title si parent && label_field_name
      if (property.parent) {
        property.title = property.title || property.parent.title;
        property.description = property.parent.description;
      }

      // ?? traiter ça dans list form ???
      if (property.schema_code) {
        property.type = 'list_form';
      }

      this._properties[this.propertyKey(context, layout)] = property;

      return property;
    }

    if (utils.isObject(layout)) {
      const computedLayout: any = {};
      for (const [key, element] of Object.entries(layout)) {
        computedLayout[key] = this.evalLayoutElement({
          element,
          layout,
          data,
          context,
        });
      }

      if (computedLayout.key && context.module_code && context.object_code) {
        const property = this._mObject.property(context, computedLayout.key);
        return {
          ...property,
          ...computedLayout,
        };
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
    const {layout, data, globalData, utils, context, formGroup, o} = x;
    ${strFunction.substr(1)}
    `;

    const f = new Function('x', strFunction);
    return f;
  }

  evalLayoutElement({ element, layout, data, context }) {
    if (!this._utils) {
      this.initUtils();
    }

    if (typeof element == 'function') {
      const globalData = data;
      const localData = utils.getAttr(globalData, context.keys);
      const formGroup = context.form_group_id && this._formControls[context.form_group_id];
      const val = element({
        layout,
        data: localData,
        globalData,
        utils: this._utils,
        o: this._utilsObject,
        context,
        formGroup,
      });
      return val !== undefined ? val : null; // on veut eviter le undefined
    }

    if (this.isStrFunction(element)) {
      try {
        return this.evalLayoutElement({
          element: this.evalFunction(element),
          context,
          layout,
          data,
        });
      } catch (exeption) {
        if (!data && `${exeption}` == 'TypeError: data is undefined') {
        } else {
          console.error(`Erreur '${exeption}' dans l'évaluation de la fonction\n${element}\n`);
        }
      }
    }
    return element;
  }

  /**
   * pour traduire un layout en formDef (pour les dynamic_form)
   */
  toFormDef(layout) {
    const formDef = utils.copy(layout);
    formDef.attribut_label = formDef.attribut_label;
    formDef.attribut_name = formDef.attribut_name || layout.key;
    return formDef;
  }

  getLayoutType = (layout) => {
    const layoutType = !layout
      ? null
      : Array.isArray(layout)
      ? 'items'
      : ['array', 'dict', 'map', 'medias'].includes(layout.type)
      ? layout.type
      : typeof layout == 'string' || layout.key
      ? 'key'
      : !layout.type
      ? layout.code
        ? 'code'
        : 'section'
      : layout.type;
    return layoutType;
  };

  getLayoutFields(layout, context, data, baseKey = null) {
    const layoutType = this.getLayoutType(layout);
    /** section */
    if (['section', 'form'].includes(layoutType)) {
      return utils.flatAndRemoveDoublons(
        this.getLayoutFields(layout.items || [], context, data, baseKey)
      );
    }

    /** items */
    if (layoutType == 'items') {
      return utils.flatAndRemoveDoublons(
        layout.map((l) => this.getLayoutFields(l, context, data, baseKey))
      );
    }
    /** key - array ou object */

    if (['array', 'dict'].includes(layoutType)) {
      const newBaseKey = baseKey ? `${baseKey}.${layout.key}` : layout.key;
      return utils.flatAndRemoveDoublons(
        this.getLayoutFields(layout.items, context, data, newBaseKey)
      );
    }

    /** key */

    let key = typeof layout == 'string' ? layout : layout.key ? layout.key : null;

    key = this.evalLayoutElement({
      element: key,
      layout: layout,
      data,
      context,
    });

    if (!key) {
      return [];
    }

    let keys = [key];

    if (layout.additional_fields) {
      keys = [...keys, ...layout.additional_fields.map((k) => `${key}.${k}`)];
    }

    return keys.map((k) => (baseKey ? `${baseKey}.${k}` : k));
  }
}
