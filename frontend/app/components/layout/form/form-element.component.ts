import { Component, OnInit, OnChanges, Injector } from '@angular/core';
import { ModulesLayoutComponent } from '../base/layout.component';
import { distinctUntilChanged, debounceTime } from 'rxjs/operators';

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
      if (!this._subs['dynChange']) {
        this._subs['dynChange'] = this.formControl.valueChanges
          .pipe(debounceTime(50))
          .subscribe((change) => {
            setTimeout(() => {
              this._mLayout.reComputeLayout('dyn change');
            }, 50);
          });
      }
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
