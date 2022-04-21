import { Component, OnInit } from "@angular/core";
import { ModulesLayoutService } from "../../services/layout.service";
import { ModulesLayoutComponent } from "./layout.component";

@Component({
  selector: "modules-layout-key",
  templateUrl: "layout-key.component.html",
  styleUrls: ["../base/base.scss", "layout-key.component.scss"],
})
export class ModulesLayoutKeyComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  constructor(_mLayout: ModulesLayoutService) {
    super(_mLayout);
    this._name = "layout-key";
  }
}
