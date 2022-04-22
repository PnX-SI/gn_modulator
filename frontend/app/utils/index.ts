/**
 * index pour regrouper les fonction utils
 */

import utilsDom from './dom';
import utilsCommons from './commons';
import utilsForm from './form';

export default {
  ...utilsCommons,
  ...utilsDom,
  ...utilsForm
}