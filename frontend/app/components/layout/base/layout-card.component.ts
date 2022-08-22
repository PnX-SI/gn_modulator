import { Component, OnInit, Injector } from "@angular/core";
import { ModulesLayoutService } from "../../../services/layout.service";
import { ModulesLayoutComponent } from "./layout.component";

@Component({
  selector: "modules-layout-card",
  templateUrl: "layout-card.component.html",
  styleUrls: ["../../base/base.scss", "layout-card.component.scss"],
})
export class ModulesLayoutCardComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-card";
  }
}
