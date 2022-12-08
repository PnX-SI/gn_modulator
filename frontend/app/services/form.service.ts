import { Injectable } from '@angular/core';
import {
  FormBuilder,
  Validators,
  ValidatorFn,
  ValidationErrors,
  AbstractControl,
} from '@angular/forms';
import { ModulesLayoutService } from './layout.service';
import utils from '../utils';

@Injectable()
export class ModulesFormService {
  constructor(private _formBuilder: FormBuilder, private _mLayout: ModulesLayoutService) {}

  /** Configuration */

  init() {}

  /** Initialise un formGroup à partir d'un layout */
  initForm(layout) {
    const formGroup = this.formGroup(layout);
    return formGroup;
  }

  formValidators(layout) {
    const validators = [];
    if (layout.required) {
      validators.push(Validators.required);
    }
    if (![undefined, null].includes(layout.min)) {
      validators.push(Validators.min(layout.min));
    }
    if (![undefined, null].includes(layout.max)) {
      validators.push(Validators.max(layout.max));
    }
    if (layout.type == 'integer') {
      validators.push(this.integerValidator());
    }

    return validators;
  }

  formDefinition(layout) {
    if (layout.type == 'array') {
      return this.formArray(layout);
    }
    if (layout.type == 'object') {
      return this.formGroup(layout.items);
    }

    let formDefinition = [null];
    return formDefinition;
  }

  formGroup(layout) {
    let formGroupDefinition = {};
    for (let elem of utils.flatLayout(layout)) {
      formGroupDefinition[elem.key] = this.formDefinition(elem);
    }
    let control = this._formBuilder.group(formGroupDefinition);
    return control;
  }

  formArray(layout) {
    let formArrayDefinition = [];
    return this._formBuilder.array(formArrayDefinition);
  }

  // renvoie le form group correspondant à context.data_keys
  getFormGroup(context): any {
    let formGroup = context.form_group;

    for (const dataKey of context.data_keys || []) {
      formGroup = Number.isInteger(dataKey) ? formGroup.at(dataKey) : formGroup.get(dataKey);
    }

    return formGroup;
  }

  // renvoie le data correspondant à context.data_keys
  getData(context, data): any {
    return utils.getAttr(data, context.data_keys);
  }

  setControls({ context, data, layout }) {
    for (let elem of utils.flatLayout(layout)) {
      this.setControl({ context, data, layout: elem });
    }

    const localData = this.getData(context, data);
    if (localData) {
      this.getFormGroup(context).patchValue(localData);
    }
  }

  /** configure un control en fonction d'un layout */
  setControl({ context, data, layout }) {
    const formGroup = this.getFormGroup(context);
    let control = formGroup.get(layout.key);
    // console.assert(!!control, { key: layout.key, control: Object.keys(formGroup.value) });
    let computedLayout = this._mLayout.computeLayout({
      layout,
      data,
      context,
    });
    control.setValidators(this.formValidators(computedLayout));
    if (computedLayout.disabled) {
      control.disable();
    }

    // control pour object
    if (layout.type == 'dict') {
      const objectContext = { ...context };
      objectContext.data_keys.push(layout.key);
      this.setControls({ context: objectContext, data, layout: layout.items });
    }

    // control pour array
    if (layout.type == 'array') {
      let controlData = (data || {})[layout.key] || [];
      if (controlData.length == control.value.length) {
        return;
      }

      control.clear();
      for (let [index, elem] of Object.entries(controlData)) {
        let elemControl = this.formGroup(layout.items);
        // this.setControls(elemControl, layout.items, elem, globalData);
        const data_keys = utils.copy(context.data_keys) || [];
        data_keys.push(layout.key);
        const arrayItemContext = {
          form_group: context.form_group,
          data_keys,
        };
        control.push(elemControl);
        this.setControls({ context: arrayItemContext, data, layout: data.items });
      }
    }

    // valeurs par defaut
    if (computedLayout.default && [null, undefined].includes(control.value)) {
      control.setValue(computedLayout.default);
      data[computedLayout.key] = computedLayout.default;
    }

    // ?? correction float int date etc
    if (
      computedLayout.type == 'date' &&
      ![null, undefined].includes(control.value) &&
      !(control.value instanceof Date)
    ) {
      data[computedLayout.key] = new Date(control.value).toISOString().split('T')[0];
      control.setValue(data[computedLayout.key]);
    }

    if (
      ['integer', 'number'].includes(computedLayout.type) &&
      ![null, undefined].includes(control.value) &&
      typeof control.value != 'number'
    ) {
      const correctValue =
        computedLayout.type == 'integer' ? parseInt(control.value) : parseFloat(control.value);

      data[computedLayout.key] = correctValue;

      control.setValue(correctValue);
    }
  }

  /** pour mettre à jour les données sans casser les références */
  updateData(data, formValue) {
    if (utils.fastDeepEqual(data, formValue)) {
      return data;
    }

    if (utils.isObject(formValue)) {
      data = data || {};
      if (!utils.isObject(data)) {
        data = formValue;
      }
      for (let [k, v] of Object.entries(formValue)) {
        data[k] = this.updateData(data[k], v);
      }
      for (let [k, v] of Object.entries(data)) {
        if (!(k in formValue)) {
          delete data[k];
        }
      }

      return data;
    }

    if (Array.isArray(formValue)) {
      data = data || [];
      let out = [];

      if (formValue.length == data.length) {
        for (let [index, elem] of data.entries()) {
          data[index] = this.updateData(elem, formValue[index]);
        }
        return data;
      } else {
        return formValue;
      }
    }

    return formValue;
  }

  isEqual(formValue, data) {
    return utils.isObject(formValue)
      ? !utils.isObject(data)
        ? false
        : Object.entries(formValue).every(([k, v]) => this.isEqual(v, data[k]))
      : Array.isArray(formValue)
      ? !Array.isArray(data)
        ? false
        : formValue.length != data.length
        ? false
        : formValue.every((elem) => data.find((d) => this.isEqual(elem, d)))
      : formValue == data;
  }

  integerValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      return control.value && parseInt(control.value) != control.value
        ? { integer: { value: control.value } }
        : null;
    };
  }
}
