import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  SimpleChanges,
} from "@angular/core";
import { ModulesFormService } from "../../services/form.service";
import { FormArray, FormGroup, FormBuilder } from "@angular/forms";

import utils from "../../utils";
import { ModulesLayoutService } from "../../services/layout.service";
import { ModulesLayoutComponent } from "../layout/layout.component";

@Component({
  selector: "modules-generic-form",
  templateUrl: "generic-form.component.html",
  styleUrls: ["../base/base.scss", "generic-form.component.scss"],
})
export class ModulesGenericFormComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  /** Mise en page du formulaire */

  listenToChanges: boolean;

  formGroup: FormGroup;

  constructor(
    private _formService: ModulesFormService,
    _layoutService: ModulesLayoutService
  ) {
    super(_layoutService);
    this._name = "form";
  }

  postProcessLayout() {
    this.initForm();
    this.updateForm();
  }

  updateForm() {
    if(!this.formGroup) {
      return;
    }
    this.listenToChanges = false;
    this._formService.setControls(this.formGroup, this.layout, this.data, this.globalData);
    this.listenToChanges = true;
  }

  onFormGroupChange(value) {
    if (
      !this.listenToChanges ||
      this._formService.isEqual(this.formGroup.value, this.data)
    ) {
      return;
    }
    // pour ne pas casser la référence à data

    this._formService.updateData(this.data, this.formGroup.value);

    this.updateForm();
    this.emitAction({type:'data-change'});
    this._mLayout.reComputeLayout();
    this.computedLayout.change && this.computedLayout.change();
  }

  postComputeLayout(): void {
    this.updateForm();

  }

  initForm() {
    if (this.formGroup) {
      return;
    }
    this.formGroup = this.formGroup || this._formService.initForm(this.layout);
    this.options = {
      ...this.options,
      form: true,
      appearance: this.layout.appearance,
      formGroup: this.formGroup
    };
    this._formService.setControls(this.formGroup, this.layout, this.data, this.globalData)
    this.formGroup.valueChanges.subscribe((value) => {
      this.onFormGroupChange(value);
    });
  }
}
