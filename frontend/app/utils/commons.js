import * as fastDeepEqual from "@librairies/fast-deep-equal/es6";
import _ from "lodash";

// const fastDeepEqual = (obj1, obj2) => {
//   return fastDeepEqual_(obj1, obj2) || fastDeepEqual_(copy(obj1), copy(obj2))
// }

const isObject = (obj) => {
  return typeof obj === "object" && !Array.isArray(obj) && obj !== null;
};

const copy = (obj) => {
  // return _.cloneDeep(obj);
  if (!obj) {
    return obj;
  }
  return JSON.parse(JSON.stringify(obj));
};

const getAttr = (obj, paths) => {
  if (!paths) {
    return obj;
  }

  if (!obj) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((elem) => getAttr(elem, paths));
  }

  const vPaths = paths.split(".");
  const path = vPaths.shift();
  const nextPaths = vPaths.join(".");
  const inter = obj[path];

  return getAttr(inter, nextPaths);
};

const parseJSON = (txt) => {
  try {
    return JSON.parse(txt);
  } catch {
    return null;
  }
};

const condAttr = (obj, paths, value) => {
  // on est au bout du chemin -> test sur les valeurs
  if (!paths) {
    return obj == value;
  }

  if (Array.isArray(obj)) {
    const cond = obj.some((elem) => condAttr(elem, paths, value));
    return cond;
  }

  const vPaths = paths.split(".");
  const path = vPaths.shift();
  const nextPaths = vPaths.join(".");
  const inter = obj[path];

  const cond = condAttr(inter, nextPaths, value);

  return cond;
};

const filtersAttr = (obj, filters) => {
  var obj_ = copy(obj);
  for (const filter of filters) {
    obj_ = filterAttr(obj_, filter.key, filter.value);
  }
  return obj_;
};

const filterAttr = (obj, paths, value) => {
  if (!condAttr(obj, paths, value)) {
    return;
  }

  if (!paths) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.filter((elem) => condAttr(elem, paths, value));
  }

  const vPaths = paths.split(".");
  const path = vPaths.shift();
  const nextPaths = vPaths.join(".");
  const inter = obj[path];

  obj[path] = filterAttr(inter, nextPaths, value);

  return obj;
};

const setAttr = (obj, paths, value) => {
  var inter = obj;
  const v_path = Object.entries(paths.split("."));
  for (const [index, path] of v_path) {
    if (index < v_path.length - 1) {
      inter[path] = inter[path] || {};
      if (!isObject(inter)) {
        console.error(`setAttr ${obj} ${paths} ${path}`);
        return;
      }
      inter = inter[path];
    } else {
      inter[path] = value;
    }
  }
};

const flat = (array) => {
  return [].concat.apply([], array);
};

const removeDoublons = (array) => {
  return array.filter(function (item, pos, self) {
    const index = self.findIndex((elem) => fastDeepEqual(item, elem));
    return index == pos;
  });
  //  return [... new Set(array)]
};

const flatAndRemoveDoublons = (array) => {
  return removeDoublons(flat(array));
};

const unaccent = (str) => str.normalize("NFD").replace(/\p{Diacritic}/gu, "");

const lowerUnaccent = (str) =>
  str &&
  str
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();

const capitalize = (s) => {
  return s && s[0].toUpperCase() + s.slice(1);
};

// remplacer dans strTest, strReplace dans un dict, array, string
const replace = (obj, strTest, strReplace) => {
  if (isObject(obj)) {
    const out = {};
    for (const [key, value] of Object.entries(obj)) {
      out[key] = replace(obj[key], strTest, strReplace);
    }
    return out;
  }

  if (Array.isArray(obj)) {
    return obj.map((elem) => replace(elem, strTest, strReplace));
  }

  if (typeof obj == "string") {
    return obj.replace(strTest, strReplace);
  }

  return obj;
};

// renvoie la date d'aujourd'hui
const today = () => {
  const today = new Date();
  return `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
};

const processFilterArray = (filters) => {
  const filtersOut = filters
    .map((f) =>
      isObject(f)
        ? f.type == "in"
          ? `${f.field}_${f.type}_${f.value.join(";")}`
          : `${f.field}_${f.type}_${f.value}`
        : f
    )
    .join(",");
    console.log(filters, filtersOut)
    return filtersOut
};

const JSONStringify = (obj) => JSON.stringify(obj, null, 4);
export default {
  fastDeepEqual,
  copy,
  filterAttr,
  filtersAttr,
  flat,
  flatAndRemoveDoublons,
  getAttr,
  isObject,
  removeDoublons,
  setAttr,
  unaccent,
  lowerUnaccent,
  parseJSON,
  processFilterArray,
  JSONStringify,
  replace,
  today,
  capitalize,
  JSON,
};
