import { Component, OnInit } from "@angular/core";

import { ModulesService } from "../../services/all.service";

import { of } from "@librairies/rxjs";
import { BaseComponent } from "./base.component";

import utils from "../../utils"
@Component({
  selector: "modules-base-properties",
  templateUrl: "base-properties.component.html",
  styleUrls: ["base.scss", "base-properties.component.scss"],
})
export class BasePropertiesComponent extends BaseComponent implements OnInit {

  dataSource = null;
  displayedColumns = null;
  bEditAllowed=false;

  layout;
  processedLayout;

  constructor(
    _services: ModulesService
  ) {
    super(_services)
    this._name = 'BaseProperties';
  }

  ngOnInit() {
    this.initHeight()
  }

  getData() {
    if(!this.value) {
      return of(null)
    }

    // console.log(this.layout[1].items)
    const fields = this._services.mLayout.getLayoutFields(this.layout)
    if(!fields.includes(this.pkFieldName())) {
      fields.push(this.pkFieldName());
    }

    if (this.hasGeometry() && !fields.includes(this.geometryFieldName())) {
      fields.push(this.geometryFieldName());
    }

    fields.push('cruved_ownership')

    return this._services.mData.getOne(
      this.schemaName,
      this.value,
      {
        fields
      }
    );
  }

  processConfig(): void {
      this.layout = this.schemaConfig.details.layout;
  }

  processData(data) {
    this.data = data;
    this.layoutData = this._services.mLayout.getLayoutData(this.layout, this.data, this.schemaConfig.definition);
    this.bEditAllowed = data['cruved_ownership'] <= this.moduleConfig.module.cruved['U'];
    this.setLayersData(true);
  }

  setComponentTitle(): void {
      this.componentTitle = `Propriétés ${this.schemaConfig.display.prep_label} ${this.pkFieldName()}=${this.value}`;
   }

  setLayersData(flyToPoint=false) {
    const properties = {
      id: this.id()
    };
    const geometry = this.data[this.geometryFieldName()];
    if (!geometry) {
      return;
    }
    if(flyToPoint) {
      this._services.mapService.waitForMap(this.mapId).then(()=> {
        const filters = {}
        filters[this.pkFieldName()] = this.id();
        this._services.mapService.findLayer(this.mapId, filters);
      });
    }
    this.layersData = {
      geomEdit: {
        geojson: {
          type: 'Feature',
          geometry,
          properties
        },
        layerOptions: {
          type: 'marker',
        }
      }
    }
  }

  onEditClick() {
    this.emitEvent({
      action: 'edit',
      params: {
        value: this.id()
      }
    });
  }

}
