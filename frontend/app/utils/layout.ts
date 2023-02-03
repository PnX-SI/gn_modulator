import utils from '.';
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

// const processData = (data, layout) => {
//   for (let elem of flatLayout(layout)) {
//     if (elem.key && elem.type == 'number') {
//       data[elem.key] = data[elem.key] ? parseFloat(data[elem.key]) : data[elem.key];
//     }
//   }
//   return data;
// };

/** Met à plat tous les layouts
 *
 * TODO array
 */

// const flatData = (data, baseKey = null) => {
//   if (utilsCommons.isObject(data)) {
//     const dataOut = {};
//     for (const [key, value] of Object.keys(data)) {
//       const newBaseKey = baseKey ? `${baseKey}.${key}` : key;
//       dataOut[newBaseKey] = flatData(value)
//     }
//     return dataOut
//   }

//   // TODO array ?

//   return data

// };

export default {
  getLayoutType,
  // processData,
};
