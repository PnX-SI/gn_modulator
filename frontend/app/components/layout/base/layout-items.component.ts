import { Component, OnInit, Injector, Input } from "@angular/core";
import { ModulesFormService } from "../../../services/form.service";

import { ModulesLayoutComponent } from "./layout.component";
@Component({
  selector: "modules-layout-items",
  templateUrl: "layout-items.component.html",
  styleUrls: ["../../base/base.scss", "layout-items.component.scss"],
})
export class ModulesLayoutItemsComponent
  extends ModulesLayoutComponent
  implements OnInit
{

  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-items";
  }

}
