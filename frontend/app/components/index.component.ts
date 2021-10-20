import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ModulesConfigService } from "../services/config.service";

@Component({
  selector: "modules-index",
  templateUrl: "index.component.html",
  styleUrls: ["index.component.scss"],
})
export class ModulesIndexComponent implements OnInit {

  schemaGroups = [];

  constructor(
    private _mConfig: ModulesConfigService,
  ) {
    this._mConfig.getSchemaGroups().subscribe((schemaGroups:Array<any>) => { this.schemaGroups=schemaGroups})
  }

  ngOnInit() {

  }

}
