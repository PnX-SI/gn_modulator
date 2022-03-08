import { Component, OnInit, Input } from "@angular/core";
import { ModulesService } from "../../services/all.service";
import { BaseComponent } from "./base.component";

@Component({
  selector: "modules-page-element",
  templateUrl: "page-element.component.html",
  styleUrls: ["base.scss", "page-element.component.scss"],
})
export class PageElementComponent extends BaseComponent implements OnInit  {

    @Input() elementType: string;

    constructor(
      _services: ModulesService
        ) {
    super(_services)
    this._name="PageElement"
    };

    ngOnInit() {
    }

    onComponentInitialized() {
    }

    processEvent(event) {

      const action = this.actions[event.action]
      console.log(action, event, this.actions)

      if (!action) {
        return;
      }

      if(action.type == 'link') {
        return this._services.mRoute.navigateToPage(this.moduleName, action.pageName, event.params)
      }

      if(action.type == 'export') {
        return this._services.mData.export(event.module_code, event.export_code);
      }

    }

}