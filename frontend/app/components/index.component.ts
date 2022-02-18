import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";
import { ModulesRouteService } from "../services/route.service";

@Component({
  selector: "modules-index",
  templateUrl: "index.component.html",
  styleUrls: ["index.component.scss"],
})
export class ModulesIndexComponent implements OnInit {

  schemaGroups = {};
  groups = [];
  modules;

  constructor(
    private _mConfig: ModulesConfigService,
    private _mRoute: ModulesRouteService,
  ) {

    this._mConfig.getModules()
      .subscribe( (modules) => {
        this.modules = Object.values(modules);
      });
  }

  ngOnInit() {

  }

}
