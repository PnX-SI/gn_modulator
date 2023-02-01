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
    if (this.computedLayout.type == 'dyn_form') {
      this.formDef = this._mLayout.toFormDef(this.computedLayout);
    }
  }

  onCheckboxChange(event) {
    this.formControl.patchValue(event);
  }

  onInputChange() {
    if (this.computedLayout.type == 'number') {
      this.formControl.patchValue(parseFloat(this.formControl.value));
      this.data[this.computedLayout.key] = this.formControl.value;
    }
    if (this.computedLayout.type == 'integer') {
      this.formControl.patchValue(parseInt(this.formControl.value));
      this.data[this.computedLayout.key] = this.formControl.value;
    }

    this.computedLayout.change && this.computedLayout.change();
  }
}
