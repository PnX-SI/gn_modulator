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
  layout: {}
  constructor(
    private _mConfig: ModulesConfigService,
    private _mRoute: ModulesRouteService,
  ) {

  }
  ngOnInit() {
    this._mConfig.getModules()
      .subscribe( (modules) => {
        this.modules = Object.values(modules);
        console.log(this.modules)
        this.layout={
          title: "Liste des modules",
          class: "modules",
          height_auto: true,
          items: [
            {
              direction: "row",
              class: 'modules-liste',
              items: this.modules.map(module => ({
                flex: 'inherit',
                title: module.module.module_label,
                description: module.module.module_desc,
                // href: this._mConfig.urlApplication() + "/#/" + module.module.module_path,
                href: "/" + module.module.module_path,
                img: this._mConfig.assetsDirectory() + '/' + module.module.module_code.toLowerCase() + "/module.jpg",
                type: 'card',
                class: 'module-card'
              }))
            }
          ]
        }
      });

  }

}
