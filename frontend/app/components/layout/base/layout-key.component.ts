import { Component, OnInit, Injector } from "@angular/core";
import { ModulesLayoutComponent } from "./layout.component";

@Component({
  selector: "modules-layout-key",
  templateUrl: "layout-key.component.html",
  styleUrls: ["../../base/base.scss", "layout-key.component.scss"],
})
export class ModulesLayoutKeyComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-key";
  }
}
