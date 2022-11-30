/**
 * index pour regrouper les fonction utils
 */

import utilsDom from './dom';
import utilsCommons from './commons';
import utilsForm from './form';
import utilsRefGeo from './ref-geo';
import utilsLayout from './layout';

export default {
  ...utilsCommons,
  ...utilsDom,
  ...utilsForm,
  ...utilsRefGeo,
  ...utilsLayout,
};
