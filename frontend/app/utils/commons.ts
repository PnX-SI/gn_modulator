import * as fastDeepEqual from '@librairies/fast-deep-equal/es6';
import _ from 'lodash';
import YML from 'js-yaml';

// const fastDeepEqual = (obj1, obj2) => {
//   return fastDeepEqual_(obj1, obj2) || fastDeepEqual_(copy(obj1), copy(obj2))
// }

/** renvoie true si obj est un object */
const isObject = (obj) => {
  return typeof obj === 'object' && !Array.isArray(obj) && obj !== null;
};

/** revoie true si obj est un fichier (File) */
const isFile = (obj) => {
  return isObject(obj) && obj.name && obj.type && obj.lastModified && obj.size;
};

const copy = (obj) => {
  // return _.cloneDeep(obj);
  if (!obj) {
    return obj;
  }

  try {
    return JSON.parse(JSON.stringify(obj));
  } catch (e) {
    console.error('erreur copy', obj, e);
  }
};

const addKey = (keys, key) => {
  for (const k of key.split('.')) {
    keys.push(k);
  }
  return keys;
};

const getAttr = (obj, paths, index = 0) => {
  if (paths == null && index == 0) {
    console.log('????? GetAtrr');
    console.trace();
  }
  if (paths == null) {
    return obj;
  }

  if (!obj) {
    return obj;
  }

  if (!Array.isArray(paths)) {
    return getAttr(obj, paths.split('.'));
  }

  if (paths.length == 0) {
    return obj;
  }

  if (index >= paths.length) {
    return obj;
  }

  let path = paths[index];
  if (Number.isInteger(Number.parseInt(path))) {
    path = Number.parseInt(path);
  }

  if (Array.isArray(obj) && !Number.isInteger(path)) {
    return obj.map((elem) => getAttr(elem, paths, index));
  }

  const inter = obj[path];
  index += 1;

  return getAttr(inter, paths, index);
};

const parseJSON = (txt) => {
  try {
    return JSON.parse(txt);
  } catch {
    return null;
  }
};

const parseYML = (txt) => {
  try {
    return YML.load(txt);
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

  const vPaths = paths.split('.');
  const path = vPaths.shift();
  const nextPaths = vPaths.join('.');
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

  const vPaths = paths.split('.');
  const path = vPaths.shift();
  const nextPaths = vPaths.join('.');
  const inter = obj[path];

  obj[path] = filterAttr(inter, nextPaths, value);

  return obj;
};

const setAttr = (obj, paths, value) => {
  var inter = obj;
  const v_path = Array.isArray(paths)
    ? Object.entries(paths)
    : (Object.entries(paths.split('.')) as any);
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

const unaccent = (str) => str.normalize('NFD').replace(/\p{Diacritic}/gu, '');

const lowerUnaccent = (str) =>
  str &&
  str
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
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

  if (typeof obj == 'string') {
    if (obj == strTest) {
      return strReplace;
    }

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
    ? filters
        .map((f) =>
          isObject(f)
            ? f.type == 'in'
              ? `${f.field} ${f.type} ${f.value.join(';')}`
              : `${f.field} ${f.type} ${f.value}`
            : f,
        )
        .join(',')
    : '';
  return filtersOut;
};

const JSONStringify = (obj) => JSON.stringify(obj, null, 4);

const numberForHuman = (x, prec = 0) => {
  const fPrec = Math.pow(10, prec);

  const params = [
    { grandeur: 1e9, lettre: 'G' },
    { grandeur: 1e6, lettre: 'M' },
    { grandeur: 1e3, lettre: 'K' },
  ];

  for (const p of params) {
    if (x > p.grandeur) {
      return `${Math.round((x / p.grandeur) * fPrec) / fPrec}${p.lettre}`;
    }
  }
  return x;
};

export default {
  addKey,
  copy,
  capitalize,
  fastDeepEqual,
  filterAttr,
  filtersAttr,
  flat,
  flatAndRemoveDoublons,
  getAttr,
  isObject,
  isFile,
  JSON,
  JSONStringify,
  lowerUnaccent,
  numberForHuman,
  parseJSON,
  parseYML,
  processFilterArray,
  unaccent,
  removeDoublons,
  replace,
  setAttr,
  today,
  YML,
};
