import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";

import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"

import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { BaseComponent } from "./base.component";
@Component({
  selector: "modules-base-properties",
  templateUrl: "base-properties.component.html",
  styleUrls: ["base.scss", "base-properties.component.scss"],
})
export class BasePropertiesComponent extends BaseComponent implements OnInit {

  dataSource = null;
  displayedColumns = null;

  layout;
  processedLayout;
  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _mForm: ModulesFormService,
    _router: Router,
    _mRoute: ModulesRouteService,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute)
    this._name = 'BaseProperties';

  }

  ngOnInit() {
  }

  getData() {
    if(!this.value) {
      return of(null)
    }

    const fields = this.getLayoutFields(this.layout)
    if (this.hasGeometry) {
      fields.push(this.geometryFieldName());
    }
    return this._mData.getOne(
      this.schemaName,
      this.value,
      {
        fields
      }
    );
  }

  processConfig(): void {
      this.layout = this.schemaConfig.details.layout;
      // this.layout = this._mForm.processLayout(this.schemaConfig.details.layout)
  }

  processData(data) {
    this.data = data;
    this.layoutData = {};
    for (const field of this.getLayoutFields(this.layout)) {
      const property = this.schemaConfig.schema.properties[field];
      this.layoutData[field] = {
        label: property.label,
        value: this.data[field]
      }
    }
    // this.dataSource = this.schemaConfig.utils.columns_array.map(
    //   p => ({
    //     name: p.name,
    //     label: p.label,
    //     type: p.type,
    //     value: this.data[p.name]
    //   })
    // );
    // this.displayedColumns = ['name', 'label', 'type', 'value']
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
    if(flyToPoint) {
      this._mapService.waitForMap(this.mapId).then(()=> {
        this._mapService.setCenter(this.mapId, [ geometry.coordinates[1], geometry.coordinates[0] ]);
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


}