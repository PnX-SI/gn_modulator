import { Injectable, Injector } from "@angular/core";
import utils from "../utils";
import layer from "./map/layer";
import { Subject } from "@librairies/rxjs";
import { ModulesConfigService } from "../services/config.service";

@Injectable()
export class ModulesLayoutService {
  _mConfig: ModulesConfigService;
  utils;

  // pour pouvoir faire passer des infos au layout
  // - par exemple sur l'utilisateur courant ou autres
  _meta:any = {};

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
  }

  $reComputeLayout = new Subject();
  $reComputedHeight = new Subject();
  $reDrawElem = new Subject();
  modals = {};
  $closeModals = new Subject();

  meta() {
    return this._meta;
  }

  initModal(modalName) {
    if (!this.modals[modalName]) {
      this.modals[modalName] = new Subject();
    }
  }

  openModal(modalName, data) {
    console.log('this.openModal', modalName, data, this.modals)
    this.modals[modalName] && this.modals[modalName].next(data);
  }

  closeModals() {
    this.$closeModals.next();
  }

  getLayoutFromName(layoutName) {
    return this._mConfig.getLayout(layoutName);
    // from config ??
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


  /** Met à plat tous les layouts
   *
   * TODO array
   */
  flatLayout(layout) {
    if (Array.isArray(layout)) {
      return utils
        .flatAndRemoveDoublons(layout.map((elem) => this.flatLayout(elem)))
        .filter((x) => !!x);
    }
    if (utils.isObject(layout)) {
      if ("key" in layout && layout.key) {
        return layout;
      }
      if ("items" in layout) {
        return this.flatLayout(layout.items);
      }
    }
  }

  /**
   * groupe:
   * obj:
   * array:
   */
  getLayoutType(layout) {
    const layoutType = !layout
      ? null
      : Array.isArray(layout)
      ? "items"
      : [
          "breadcrumbs",
          "button",
          "html",
          "form",
          "message",
          "medias",
          "card",
          "object",
          "table",
          "map",
          "modal",
          "dict"
        ].includes(layout.type)
      ? layout.type
      : layout.key
      ? "key"
      : layout.layout_name
      ? "name"
      : "section";
    return layoutType;
  }

  /**
   * Renvoie tous les champs d'un layout
   */
  getLayoutFields(layout, baseKey = null) {
    const layoutType = this.getLayoutType(layout);
    /** section */
    if (["section", "form"].includes(layoutType)) {
      return utils.flatAndRemoveDoublons(
        this.getLayoutFields(layout.items || [], baseKey)
      );
    }

    /** items */
    if (layoutType == "items") {
      return utils.flatAndRemoveDoublons(
        layout.map((l) => this.getLayoutFields(l, baseKey))
      );
    }
    /** key - array ou object */
    if (layoutType == "key" && ["array", "dict"].includes(layout.type)) {
      const newBaseKey = baseKey ? `${baseKey}.${layout.key}` : layout.key;
      return utils.flatAndRemoveDoublons(
        this.getLayoutFields(layout.items, newBaseKey)
      );
    }
    /** key */
    const keys = [layout.key];

    return keys
      .filter((k) => !!k)
      .map((key) => (baseKey ? `${baseKey}.${key}` : key));
  }

  isStrFunction(layout) {
    return typeof layout == "string"
      ? "__f__" == layout.substr(0, 5)
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
          ? this.evalLayout({ layout: value, data, globalData, formGroup, meta: this._meta })
          : value;
      }
      return computedLayout;
    }

    return layout;
  }

  evalFunction(layout) {
    let strFunction = Array.isArray(layout) ? layout.join("") : layout;
    strFunction = strFunction.substr(5);
    if (!strFunction.includes("return ") && strFunction[0] != "{") {
      strFunction = `{ return ${strFunction} }`;
    }

    const f = new Function(
      "data",
      "globalData",
      "formGroup",
      "utils",
      "meta",
      strFunction
    );

    return f;
  }

  evalLayout({ layout, data, globalData = null, formGroup = null, meta=null }) {
    if (this.isStrFunction(layout) && !data) {
      return null;
    }

    if (!data) {
      return layout;
    }

    if (typeof layout == "function") {
      return layout({ data });
    }

    if (this.isStrFunction(layout)) {
      const val = this.evalFunction(layout)(data, globalData, formGroup, utils, meta);
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
