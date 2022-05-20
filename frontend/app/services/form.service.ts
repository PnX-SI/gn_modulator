import { Injectable } from "@angular/core";
import {
  FormArray,
  FormGroup,
  FormBuilder,
  FormControl,
  Validators,
  ValidatorFn,
  ValidationErrors,
  AbstractControl
} from "@angular/forms";
import { ModulesLayoutService } from "./layout.service";
import utils from "../utils";

@Injectable()
export class ModulesFormService {
  constructor(
    private _formBuilder: FormBuilder,
    private _mLayout: ModulesLayoutService
  ) {}

  /** Configuration */

  init() {}

  /** Initialise un formGroup à partir d'un layout */
  initForm(layout) {
    return this.formGroup(layout);
  }

  formValidators(layout) {
    const validators = [];
    if (layout.required) {
      validators.push(Validators.required);
    }
    if(![undefined, null].includes(layout.min)) {
      validators.push(Validators.min(layout.min))
    }
    if(![undefined, null].includes(layout.max)) {
      validators.push(Validators.max(layout.max))
    }
    if(layout.type == 'integer') {
      validators.push(this.integerValidator())
    }

    return validators;
  }

  formDefinition(layout) {
    if (layout.type == "array") {
      return this.formArray(layout);
    }
    if (layout.type == "object") {
      return this.formGroup(layout.items);
    }
    let formDefinition = [null, this.formValidators(layout)];
    return formDefinition;
  }

  formGroup(layout) {
    let formGroupDefinition = {};
    for (let elem of this._mLayout.flatLayout(layout)) {
      formGroupDefinition[elem.key] = this.formDefinition(elem);
    }
    let control = this._formBuilder.group(formGroupDefinition);
    return control;
  }

  formArray(layout) {
    let formArrayDefinition = [];
    return this._formBuilder.array(formArrayDefinition);
  }

  setControls(formControl, layout, data, globalData) {
    for (let elem of this._mLayout.flatLayout(layout)) {
      this.setControl(formControl, elem, data, globalData);
    }
    if (data) {
      formControl.patchValue(data);
    }
  }

  /** configure un control en fonction d'un layout */
  setControl(formControl, layout, data, globalData) {
    let control = formControl.get(layout.key);
    let computedLayout = this._mLayout.computeLayout({layout, data, globalData, formGroup: null, elemId: null})
    control.setValidators(this.formValidators(computedLayout));
    // control pour object
    if (layout.type == "object") {
      let controlData = (data || {})[layout.key] || {};
      this.setControls(control, layout.items, controlData, globalData);
    }
    // control pour array
    if (layout.type == "array") {
      let controlData = (data || {})[layout.key] || [];
      if (controlData.length == control.value.length) {
        return;
      }

      control.clear();
      for (let elem of controlData) {
        let elemControl = this.formGroup(layout.items);
        this.setControls(elemControl, layout.items, elem, globalData);
        control.push(elemControl);
      }
    }
  }

  /** pour mettre à jour les données sans casser les références */
  updateData(data, formValue) {
    if (utils.fastDeepEqual(data, formValue)) {
      return data;
    }

    if (utils.isObject(formValue)) {
      data = data || {};
      if(!utils.isObject(data)) {
        data = formValue
      }
      for (let [k, v] of Object.entries(formValue)) {
        data[k] = this.updateData(data[k], v);
      }
      for (let [k, v] of Object.entries(data)) {
        if( ! (k in formValue)) {
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

  /** pour corriger les string t
   * en nombre ??? */
  processData(data, layout) {
    for (let elem of this._mLayout.flatLayout(layout)) {
      if (elem.key && elem.type == "number") {
        data[elem.key] = data[elem.key]
          ? parseFloat(data[elem.key])
          : data[elem.key]
      }
    }
    return data;
  }

  processAction(formGroup, layout, data, options) {
    // if (options.type == "add-array-element") {
    //   data[options.key].push({});
    //   this.setControls(formGroup, layout, data);
    //   formGroup.patchValue(data);
    // }
    // if (options.type == "remove-array-element") {
    //   this.setControls(formGroup, layout, data);
    //   data[options.key].splice(options.index, 1);
    //   // formGroup.patchValue(data);
    // }
    // if (options.type == "remove-array-element") {
    //   data[options.key] = [];
    //   this.setControls(formGroup, layout, data);
    //   formGroup.patchValue(data);
    // }
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

  integerValidator(): ValidatorFn
   {
    return (control: AbstractControl): ValidationErrors | null => {
      return control.value && parseInt(control.value) != control.value ? {integer: {value: control.value}} : null;
    };
  }
}
