import { Injectable } from '@angular/core';
import {
  FormBuilder,
  FormControl,
  Validators,
  ValidatorFn,
  ValidationErrors,
  AbstractControl,
  FormGroupDirective,
  NgForm,
} from '@angular/forms';
import { ErrorStateMatcher } from '@angular/material/core';
import { ModulesLayoutService } from './layout.service';
import { ModulesObjectService } from './object.service';
import { MediaService } from '@geonature_common/service/media.service';

import utils from '../utils';

/** Error when invalid control is dirty, touched, or submitted. */
export class MyErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (control.dirty || control.touched || isSubmitted));
  }
}

@Injectable()
export class ModulesFormService {
  matcher;
  constructor(
    private _formBuilder: FormBuilder,
    private _mLayout: ModulesLayoutService,
    private _mObject: ModulesObjectService,
    private _mediaService: MediaService
  ) {
    this.matcher = new MyErrorStateMatcher();
  }

  /** Configuration */

  init() {}

  /** Initialise un formGroup à partir d'un layout */
  initForm(layout, id, context) {
    const formGroup = this.createFormGroup(layout, context);
    this._mLayout.setFormControl(formGroup, id);
    return formGroup;
  }

  formValidators(layout, context) {
    const validators = [];
    if (layout.required && !context.skip_required) {
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
    if (layout.type_widget == 'medias') {
      validators.push(this._mediaService.mediasValidator());
    }

    return validators;
  }

  formDefinition(layout, context) {
    if (layout.type == 'array') {
      return this.formArray(layout);
    }
    // todo object dict watever ??
    if (layout.type == 'dict') {
      return this.createFormGroup(layout.items, context);
    }

    let formDefinition = [null];
    return formDefinition;
  }

  processLayout(layout, context) {
    let flat = this._mLayout.flatLayout(layout).map((elem) => {
      if (elem.key) {
        elem.key = this._mLayout.evalLayoutElement({
          element: elem.key,
          layout: elem,
          context,
          data: null,
        });
        return elem;
      } else {
        return this._mObject.property(context, elem);
      }
    });

    let simple = flat.filter((l) => !l.key.includes('.'));
    let dotted: Array<any> = flat
      .filter((l) => l.key.includes('.'))
      .map((l) => {
        const keys = l.key.split('.');
        const keyDict = keys.shift();
        return {
          type: 'dict',
          key: keyDict,
          items: [
            {
              ...l,
              key: keys.join('.'),
            },
          ],
        };
      });

    for (let [i1, l1] of Object.entries(dotted)) {
      const keyDict = l1.key;
      for (let [i2, l2] of Object.entries(dotted)) {
        if (i1 <= i2) {
          continue;
        }

        if (l2.key == l1.key) {
          l1.items.push(l2.items);
          l2.items = null;
        }
      }
    }

    dotted = dotted.filter((l) => l.items);

    return [...simple, ...dotted];
  }

  createFormGroup(layout, context): any {
    let formGroupDefinition = {};

    for (let elem of this.processLayout(layout, context)) {
      formGroupDefinition[elem.key] = this.formDefinition(elem, context);
    }
    let control = this._formBuilder.group(formGroupDefinition);
    return control;
  }

  formArray(layout) {
    let formArrayDefinition = [];
    return this._formBuilder.array(formArrayDefinition);
  }
  // renvoie le data correspondant à context.data_keys
  getData(context, data): any {
    return utils.getAttr(data, context.data_keys);
  }

  setControls({ context, data, layout }) {
    for (let elem of this.processLayout(layout, context)) {
      this.setControl({ context, data, layout: elem });
    }

    const localData = this.getData(context, data);
    const formControl = this.getFormControl(context.form_group_id, context.data_keys);
    if (localData) {
      formControl.patchValue(localData);
    } else {
      formControl.updateValueAndValidity();
    }
  }

  getFormControl(formControl, key) {
    if (formControl == null) {
      console.error('formControl est null');
      return;
    }

    if (!utils.isObject(formControl)) {
      return this.getFormControl(this._mLayout.getFormControl(formControl), key);
    }

    if (Array.isArray(key)) {
      for (let k of key) {
        formControl = this.getFormControl(formControl, k);
      }
    }

    if (typeof key == 'string') {
      if (key.includes('.')) {
        for (const k of key.split('.')) {
          formControl = this.getFormControl(formControl, k);
        }
      } else {
        if (Number.isInteger(Number.parseInt(key))) {
          formControl = formControl.at(Number.parseInt(key));
        } else {
          formControl = formControl.get(key);
        }
      }
    }

    return formControl;
  }

  /** configure un control en fonction d'un layout */
  setControl({ context, data, layout }) {
    let control = this.getFormControl(context.form_group_id, [...context.data_keys, layout.key]);
    let computedLayout = this._mLayout.computeLayout({
      layout,
      data,
      context,
    });
    control.setValidators(this.formValidators(computedLayout, context));
    // if (computedLayout.disabled) {
    // control.disable();
    // }

    // control pour object
    if (layout.type == 'dict') {
      const objectContext = { ...context };
      objectContext.data_keys = utils.copy(context.data_keys);
      utils.addKey(objectContext.data_keys, layout.key);
      this.setControls({ context: objectContext, data, layout: layout.items });
    }

    // control pour array
    if (layout.type == 'array') {
      let controlData = utils.getAttr(data || {}, [...context.data_keys, computedLayout.key]) || [];
      if (controlData.length == control.value.length) {
        return;
      }
      control.clear();
      for (let [index, elem] of Object.entries(controlData)) {
        let elemControl = this.createFormGroup(layout.items, context);
        control.push(elemControl);
        const arrayItemContext = {
          ...context,
          data_keys: utils.addKey(utils.copy(context.data_keys), `${layout.key}.${index}`),
        };
        this.setControls({ context: arrayItemContext, data, layout: layout.items });
      }
    }

    // valeurs par defaut
    if (computedLayout.default && [null, undefined].includes(control.value)) {
      control.setValue(computedLayout.default);
      if (data) {
        data[computedLayout.key] = computedLayout.default;
      }
    }

    // ?? correction float int date etc
    if (
      computedLayout.type == 'date' &&
      ![null, undefined].includes(control.value) &&
      !(control.value instanceof Date)
    ) {
      const val = new Date(control.value).toISOString().split('T')[0];
      if (data) {
        data[computedLayout.key] = val;
      }

      control.setValue(val);
    }

    if (
      ['integer', 'number'].includes(computedLayout.type) &&
      ![null, undefined].includes(control.value) &&
      typeof control.value != 'number'
    ) {
      const correctValue =
        computedLayout.type == 'integer' ? parseInt(control.value) : parseFloat(control.value);

      if (data) {
        data[computedLayout.key] = correctValue;
      }
      control.setValue(correctValue);
    }
    control.updateValueAndValidity();
    control.markAsDirty();
    control.parent.markAsDirty();
  }

  /** pour mettre à jour les données sans casser les références */
  updateData(data, formValue) {
    if (this.isEqual(formValue, data)) {
      return data;
    }

    if (utils.isFile(formValue)) {
      return formValue;
    }

    if (utils.isObject(formValue)) {
      if (data == null) {
        return formValue;
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
    return utils.isFile(formValue)
      ? utils.isFile(data)
        ? ['name', 'lastModified', 'size', 'type'].every((k) => data[k] == formValue[k])
        : false
      : utils.isObject(formValue)
      ? !utils.isObject(data)
        ? false
        : // Object.keys(formValue).length == Object.keys(data).length &&
          Object.entries(formValue)
            .filter(([k, v]) => k != 'pendingRequest')
            .every(([k, v]) => this.isEqual(v, data[k]))
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
