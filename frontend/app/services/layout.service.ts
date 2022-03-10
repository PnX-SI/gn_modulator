import { Injectable } from "@angular/core"
import utils from "../utils"

@Injectable()
export class ModulesLayoutService {

  constructor(
  ) {
  }

  /**
   * groupe:
   * obj:
   * array:
   */
   getLayoutType(layout) {
    return !layout
      ? null
      : Array.isArray(layout)
        ? 'items'
        : utils.isObject(layout) && layout.items
          ? layout.type == 'array'
            ? 'array'
            : 'obj'
          : 'key'
  };

  getLayoutFields(layout, processArray=true) {
    if (this.getLayoutType(layout) == 'array') {
        return processArray
          ? this.getLayoutFields(layout.items)
          : [layout.key]
    }

    if (this.getLayoutType(layout) == 'items') {
      return utils.flatAndRemoveDoublons(layout.map(l => this.getLayoutFields(l, processArray)))
    }
    if (this.getLayoutType(layout) == 'obj') {
      return utils.flatAndRemoveDoublons(layout.items.map(l => this.getLayoutFields(l, processArray)))
    }

    const key = layout.key_value || layout.key || layout;
    var keys = [key];
    if (layout.filters) {
      keys = [ ...keys, ...layout.filters.map(f => f.key) ];
    }
    keys = keys.map((key) => key.replace('[]', ''))
    return utils.flatAndRemoveDoublons(keys);
  };

  removeBrakets(layout) {
    if (utils.isObject(layout)) {
      const layoutOut = {}
      for (const key of Object.keys(layout)){
        layoutOut[key] = this.removeBrakets(layout[key])
      }
      return layoutOut
    }
    if (Array.isArray(layout)) {
      return layout.map(l => this.removeBrakets(l))
    }
    if (layout && layout.includes('[].')) {
      return layout.split("[].")[1]
    }
    return layout
  }

  getLayoutData(layout, data, definition=null) {
    const layoutData = {};
    for (const field of this.getLayoutFields(layout, false)) {
      layoutData[field.key || field] = this.processLayoutField(field, data, definition)
    }
    return layoutData
  }

  processLayoutField(field, data, definition=null) {
    const key = field.key || field;
    const keyValue = field.key_value || field.key || field;
    const keyProp = keyValue.split('.')[0];
    const property = definition ?
      definition.properties[keyProp]:
      {}
    ;
    const title = field.title || property.title;
    let value =
      field.filters
        ? utils.getAttr(utils.filtersAttr(data, field.filters), keyValue)
        : utils.getAttr(data, keyValue)

    // affichage des booléens
    let labels =field.labels ||property.labels;
    if (labels) {
      value = (value===true)
        ? labels[0]
        : value===false
          ? labels[0]
          : value
    }
    return {title, value }
  }

}
