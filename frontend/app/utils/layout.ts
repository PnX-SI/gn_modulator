import utilsCommons from '.';

/**
 * Fonctions pour la gestion des layouts
 */

/**
 * Renvoie le type d'un layout
 */
const getLayoutType = (layout) => {
  const layoutType = !layout
    ? null
    : Array.isArray(layout)
    ? 'items'
    : typeof layout == 'string' || layout.key
    ? 'key'
    : !layout.type
    ? layout.code
      ? 'code'
      : 'section'
    : layout.type;
  return layoutType;
};

/**
 * Renvoie tous les champs d'un layout
 */
const getLayoutFields = (layout, baseKey = null) => {
  const layoutType = getLayoutType(layout);
  /** section */
  if (['section', 'form'].includes(layoutType)) {
    return utilsCommons.flatAndRemoveDoublons(getLayoutFields(layout.items || [], baseKey));
  }

  /** items */
  if (layoutType == 'items') {
    return utilsCommons.flatAndRemoveDoublons(layout.map((l) => getLayoutFields(l, baseKey)));
  }
  /** key - array ou object */
  if (layoutType == 'key' && ['array', 'dict'].includes(layout.type)) {
    const newBaseKey = baseKey ? `${baseKey}.${layout.key}` : layout.key;
    return utilsCommons.flatAndRemoveDoublons(getLayoutFields(layout.items, newBaseKey));
  }

  /** key */
  const key = typeof(layout)   == 'string' ? layout : layout.key ? layout.key : null;

  if (!key) {
    return [];
  }

  return [baseKey ? `${baseKey}.${key}` : key];
};

const processData = (data, layout) => {
  for (let elem of flatLayout(layout)) {
    if (elem.key && elem.type == 'number') {
      data[elem.key] = data[elem.key] ? parseFloat(data[elem.key]) : data[elem.key];
    }
  }
  return data;
};

/** Met à plat tous les layouts
 *
 * TODO array
 */
const flatLayout = (layout) => {
  if (layout == null) {
    return [];
  }
  if (Array.isArray(layout)) {
    return utilsCommons
      .flatAndRemoveDoublons(layout.map((elem) => flatLayout(elem)))
      .filter((x) => !!x);
  }
  if (utilsCommons.isObject(layout)) {
    if (layout.key) {
      return [layout];
    }
    if ('items' in layout) {
      return flatLayout(layout.items);
    }
  }

  if (typeof layout == 'string') {
    return [layout];
  }
};

export default {
  getLayoutType,
  getLayoutFields,
  processData,
  flatLayout,
};
