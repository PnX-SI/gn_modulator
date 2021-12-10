import * as fastDeepEqual from '@librairies/fast-deep-equal/es6';
import { RadiosComponent } from 'angular7-json-schema-form';

const isObject = (obj) => {
  return (
    typeof obj === 'object' &&
    !Array.isArray(obj) &&
    obj !== null
  )
}

const copy = (obj) => {
  if (!obj) {
    return obj;
  }
  return JSON.parse(JSON.stringify(obj));
}

const getAttr = (obj, paths) => {
  var inter = obj;
  for (const path of paths.split('.')) {
    try {
      inter = inter[path];
    }
    catch {
      return null;
    }
  }
  return inter;
}

const setAttr = (obj, paths, value) => {
  var inter = obj
  const v_path = Object.entries(paths.split('.'));
  for (const [index, path] of v_path) {
    if (index < v_path.length -1) {
      inter[path] = inter[path] || {}
      if (!isObject(inter)) {
        console.error(`setAttr ${obj} ${paths} ${path}`)
        return
      }
    } else {
      inter[path] = value
    }
  }
}

const flat = (array) => {
  return [].concat.apply([], array);
}

export default {
  fastDeepEqual,
  copy,
  isObject,
  getAttr,
  setAttr,
  flat
}