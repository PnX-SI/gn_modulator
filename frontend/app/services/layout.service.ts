import { Injectable } from "@angular/core";
import utils from "../utils";
import layer from "./map/layer";
import { Subject } from "@librairies/rxjs";

@Injectable()
export class ModulesLayoutService {
  constructor() {}

  $reComputeLayout = new Subject();

  reComputeLayout() {
    this.$reComputeLayout.next(true);
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
      if ("key" in layout) {
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
      : layout.key
      ? "key"
      : layout.type == "button"
      ? "button"
      : "section";
    return layoutType;
  }

  /**
   * Renvoie tous les champs d'un layout
   */
  getLayoutFields(layout, baseKey = null) {
    const layoutType = this.getLayoutType(layout);

    /** section */
    if (layoutType == "section") {
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
    if (layoutType == "key" && ["array", "object"].includes(layout.type)) {
      const newBaseKey = baseKey ? `${baseKey}.${layout.key}` : layout.key;
      return utils.flatAndRemoveDoublons(
        this.getLayoutFields(layout.items, newBaseKey)
      );
    }
    /** key */
    const keys = [layout.key];
    // TODO filters ???
    return keys.map((key) => (baseKey ? `${baseKey}.${key}` : key));
  }

  //   if (this.getLayoutType(layout) == "section" && layout.type == "array") {
  //     return processArray ? this.getLayoutFields(layout.items) : [layout.key];
  //   } else if (
  //     this.getLayoutType(layout) == "section" &&
  //     layout.type == "items"
  //   ) {
  //     return utils.flatAndRemoveDoublons(
  //       layout.map((l) => this.getLayoutFields(l, processArray))
  //     );
  //   } else if (this.getLayoutType(layout) == "section") {
  //     return utils.flatAndRemoveDoublons(
  //       layout.items.map((l) => this.getLayoutFields(l, processArray))
  //     );
  //   }

  //   const key = layout.key_value || layout.key || layout;
  //   var keys = [key];
  //   if (layout.filters) {
  //     keys = [...keys, ...layout.filters.map((f) => f.key)];
  //   }
  //   keys = keys.map((key) => key.replace("[]", ""));
  //   return utils.flatAndRemoveDoublons(keys);
  // }

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

  computeLayout({ layout, data, globalData, formGroup, elemId }) {
    if (utils.isObject(layout)) {
      const computedLayout = {};
      for (const [key, value] of Object.entries(layout)) {
        if (key == "change") {
          layout[key] = value;
          continue;
        }
        computedLayout[key] = this.isStrFunction(value)
          ? this.evalLayout({ layout: value, data, globalData, formGroup })
          : value;
      }
      return computedLayout;
    }

    if (Array.isArray(layout)) {
      return this.computeLayoutHeight(layout, elemId)
    }
    return layout;
  }

  computeLayoutHeight(items, elemId) {
    const layoutIndex =
      items && items.findIndex && items.findIndex((l) => l["overflow"]);
    if ([-1, null, undefined].includes(layoutIndex) || !document
    .getElementById(`${elemId}.0`)) {
      return items;
    }

    const heightParent = document
      .getElementById(`${elemId}.0`)
      .closest(".layout-section").clientHeight;


    const heightSibblings = items
      .map((l, ind) => document.getElementById(`${elemId}.${ind}`).clientHeight)
      .filter((l, ind) => ind != layoutIndex)
      .reduce((acc, cur) => acc + cur);

    console.log('H1', heightParent, heightSibblings, items.map((l, ind) => document.getElementById(`${elemId}.${ind}`)));
    const height = heightParent - heightSibblings;
    // const height = 300;

    items[layoutIndex].style = {
      ...(items[layoutIndex].style || {}),
      "overflow-y": "scroll",
      height: `${height}px`,
    };

    return items;
  }

  // computeLayout({ layoutDefinition, data, globalData, layout }) {
  //   globalData = globalData || data;
  //   if (utils.isObject(layoutDefinition)) {
  //     layout = layout || {};

  //     for (const [key, value] of Object.entries(layoutDefinition)) {
  //       if (key == "change") {
  //         layout[key] = value;
  //         continue;
  //       }

  //       if (key == "items" && ["array", "object"].includes(layout.type)) {
  //         layout[key] = this.computeLayout({
  //           layoutDefinition: layoutDefinition[key],
  //           data: data[layout.key],
  //           globalData,
  //           layout: layout[key],
  //         });
  //         continue;
  //       }

  //       layout[key] = this.computeLayout({
  //         layoutDefinition: layoutDefinition[key],
  //         data,
  //         globalData,
  //         layout: layout[key],
  //       });
  //     }
  //     return layout;
  //   }

  //   if (Array.isArray(layoutDefinition)) {
  //     for (const index in layoutDefinition) {
  //       layout = layout || [];
  //       layout[index] = this.computeLayout(
  //         {
  //           layoutDefinitionlayoutDefinition[index],
  //         data,
  //         globalData,
  //         layout[index]
  //       );
  //     }
  //     return layout;
  //   }

  //   return this.evalLayout(layoutDefinition, data, globalData, null);
  // }

  evalFunction(layout) {
    let strFunction = Array.isArray(layout) ? layout.join("") : layout;
    strFunction = strFunction.substr(5);
    if (!strFunction.includes("return ") && strFunction[0] != "{") {
      strFunction = `{ return ${strFunction} }`;
    }
    return new Function("data", "globalData", "formGroup",  strFunction);
  }

  evalLayout({ layout, data, globalData = null, formGroup = null }) {
    if (!data) {
      return layout;
    }

    if (typeof layout == "function") {
      return layout({ data });
    }

    if (this.isStrFunction(layout)) {
      return this.evalFunction(layout)(data, globalData, formGroup);
    }
    return layout;
  }
}
