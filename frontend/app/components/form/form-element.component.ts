import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges, OnChanges } from "@angular/core";
import { FormGroup } from "@angular/forms";
import { ModulesLayoutService } from "../../services/layout.service";
import utils from '../../utils'
import { ModulesLayoutComponent } from "../layout/layout.component";

@Component({
  selector: "modules-form-element",
  templateUrl: "form-element.component.html",
  styleUrls: ["form-element.component.scss"],
})
export class ModulesFormElementComponent extends ModulesLayoutComponent implements OnInit, OnChanges{

  constructor(
    _mLayout: ModulesLayoutService
  ) {
    super(_mLayout);
    this._name = "form_element"
  };

  onCheckboxChange(event) {
    this.options.formGroup.get(this.layout.key).patchValue(event)
  }

}
