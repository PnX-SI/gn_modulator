import { Component, OnInit } from "@angular/core";
import { ModulesFormService } from "../../services/form.service";
import { ModulesLayoutService } from "../../services/layout.service";

import { ModulesLayoutComponent } from "./layout.component";
@Component({
  selector: "modules-layout-object",
  templateUrl: "layout-object.component.html",
  styleUrls: ["../base/base.scss", "layout-object.component.scss"],
})
export class ModulesLayoutObjectComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  /** options pour les elements du array */

  // arrayOptions: Array<any>;

  constructor(
    private _formService: ModulesFormService,
    _mLayout: ModulesLayoutService
    ) {
    super(_mLayout);
    this._name = "layout-object";
  }

  objectOptions() {
    return {
      ...this.options,
      formGroup: this.options.formGroup && this.options.formGroup.get(this.layout.key)
    }
  }

}
