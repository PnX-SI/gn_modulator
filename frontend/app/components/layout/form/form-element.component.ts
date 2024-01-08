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
    this.bPostComputeLayout = true;
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

  postComputeLayout(dataChanged: any, layoutChanged: any, contextChanged: any): void {}

  onCheckboxChange(event) {
    this.formControl.patchValue(event);
  }

  onUUIDChange() {
    if (this.formControl.value == '') {
      this.formControl.setValue(null);
      this.data[this.computedLayout.key] = null;
    }
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

  openInputFile() {
    document.getElementById(`${this._id}_inputfile`)?.click();
  }

  fileChange(files: File[]) {
    if (files.length) {
      this.formControl.setValue(files[0]);
      this.formControl.updateValueAndValidity();
    } else {
      this.formControl.setValue(null);
    }
  }
}
