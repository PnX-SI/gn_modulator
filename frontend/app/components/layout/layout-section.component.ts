import { Component, OnInit } from "@angular/core";
import { ModulesLayoutService } from "../../services/layout.service";
import { ModulesLayoutComponent } from "./layout.component";

@Component({
  selector: "modules-layout-section",
  templateUrl: "layout-section.component.html",
  styleUrls: ["../base/base.scss", "layout-section.component.scss"],
})
export class ModulesLayoutSectionComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  constructor(_mLayout: ModulesLayoutService) {
    super(_mLayout);
    this._name = "layout-section";
  }
}
