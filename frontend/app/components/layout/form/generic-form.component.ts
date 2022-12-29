import { Component, OnInit, Injector } from '@angular/core';
import { ModulesFormService } from '../../../services/form.service';
import { FormGroup } from '@angular/forms';

import { ModulesLayoutComponent } from '../base/layout.component';

@Component({
  selector: 'modules-generic-form',
  templateUrl: 'generic-form.component.html',
  styleUrls: ['../../base/base.scss', 'generic-form.component.scss'],
})
export class ModulesGenericFormComponent extends ModulesLayoutComponent implements OnInit {
  /** Mise en page du formulaire */

  listenToChanges: boolean;

  formGroup: FormGroup;

  _formService;

  constructor(_injector: Injector) {
    super(_injector);
    this._formService = this._injector.get(ModulesFormService);
    this._name = 'form';
    this.bPostComputeLayout = true;
  }

  postProcessLayout() {
    this.initForm();
    this.updateForm();
  }

  // processAction(event) {
  //   if (event.type == "data-change") {
  //     this.computeLayout();
  //   }
  //   if (event.type == "submit") {
  //     this.emitAction({
  //       "action": "submit",
  //       "data": this.data,
  //       "layout": this.computedLayout
  //     })
  //   }
  //   this.emitAction(event);
  // }

  updateForm() {
    if (!this.formGroup) {
      return;
    }
    this.listenToChanges = false;
    this._formService.setControls({ context: this.context, layout: this.layout, data: this.data });
    this.listenToChanges = true;
    // test du change ici ???
  }

  onFormGroupChange() {
    if (!this.listenToChanges || this._formService.isEqual(this.formGroup.value, this.data)) {
      return;
    }
    const dataChanged = {};
    for (let key of Object.keys(this.formGroup.value)) {
      if (!this._formService.isEqual(this.formGroup.value[key], this.data[key])) {
        dataChanged[key] = this.formGroup.value[key];
      }
    }

    // pour ne pas casser la référence à data
    this._formService.updateData(this.data, this.formGroup.value);

    this.updateForm();
    this.emitAction({ type: 'data-change' });
    this._mLayout.reComputeLayout('form');

    this.computedLayout.change && this.computedLayout.change(dataChanged);
  }

  postComputeLayout(dataChanged, layoutChanged): void {
    this.updateForm();
  }

  initForm() {
    if (this.formGroup) {
      return;
    }

    this.formGroup = this._mForm.initForm(this.layout, this._id, this.context);

    this.context.form_group_id = this._id;
    this.context.appearance = this.layout.appearance;
    this._formService.setControls({ context: this.context, layout: this.layout, data: this.data });
    this.formGroup.valueChanges.subscribe((value) => {
      this.onFormGroupChange();
    });
  }
}
