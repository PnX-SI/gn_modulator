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
    : ['array', 'dict', 'map'].includes(layout.type)
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
  processData,
  flatLayout,
};
