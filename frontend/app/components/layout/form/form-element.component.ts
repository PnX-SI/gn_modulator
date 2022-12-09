import { Component, OnInit, OnChanges, Injector } from '@angular/core';
import { ModulesLayoutComponent } from '../base/layout.component';

@Component({
  selector: 'modules-form-element',
  templateUrl: 'form-element.component.html',
  styleUrls: ['form-element.component.scss', '../../base/base.scss'],
})
export class ModulesFormElementComponent
  extends ModulesLayoutComponent
  implements OnInit, OnChanges
{
  /** pour les composants dynamic-form de geonature */
  formDef;
  formControl;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'form_element';
  }

  postProcessLayout(): void {
    this.formControl = this.getFormControl();
    if (this.computedLayout.type == 'dyn_form') {
      this.formDef = this._mLayout.toFormDef(this.computedLayout);
    }
  }

  onCheckboxChange(event) {
    this.getFormControl().patchValue(event);
  }

  onInputChange() {
    const formControl = this.getFormControl();

    if (this.computedLayout.type == 'number') {
      formControl.patchValue(parseFloat(formControl.value));
      this.data[this.layout.key] = formControl.value;
    }
    if (this.computedLayout.type == 'integer') {
      formControl.patchValue(parseInt(formControl.value));
      this.data[this.layout.key] = formControl.value;
    }

    this.computedLayout.change && this.computedLayout.change();
  }
}
