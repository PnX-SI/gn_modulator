import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges, OnChanges } from "@angular/core";
import { FormGroup } from "@angular/forms";
import { ModulesLayoutService } from "../../services/layout.service";
import utils from '../../utils'
import { ModulesLayoutComponent } from "../layout/layout.component";

@Component({
  selector: "modules-form-element",
  templateUrl: "form-element.component.html",
  styleUrls: ["form-element.component.scss", "../base/base.scss"],
})
export class ModulesFormElementComponent extends ModulesLayoutComponent implements OnInit, OnChanges{

  /** pour les composants dynamic-form de geonature */
  formDef;

  constructor(
    _mLayout: ModulesLayoutService
  ) {
    super(_mLayout);
    this._name = "form_element"
  };

  postProcessLayout(): void {
    if(this.computedLayout.type == 'dyn_form') {

      this.formDef = this._mLayout.toFormDef(this.computedLayout);
      console.log(this.formDef)
    }
  }
  onCheckboxChange(event) {
    this.options.formGroup.get(this.layout.key).patchValue(event)
  }

}
