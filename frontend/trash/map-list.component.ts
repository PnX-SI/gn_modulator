import { Component, OnInit } from "@angular/core";
import { BaseComponent } from "./base.component";
import { ModulesService } from "../../services/all.service";

@Component({
  selector: "modules-map-list",
  templateUrl: "map-list.component.html",
  styleUrls: [ "base.scss", "map-list.component.scss", ],
})
export class ModuleslistComponent extends BaseComponent implements OnInit {


  constructor(
    _services: ModulesService
    ) {
    super(_services)
    this._name = 'list'
  }

  ngOnInit(): void {
    this.initHeight(50);
  }

  processEvent(event) {

    this.emitEvent(event);

    if(event.action == 'filters') {
      this.filters = event.params.filters;
    }

    if(event.action == 'selected') {
      this.value = event.params.value
    }

  }

}