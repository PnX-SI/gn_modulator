import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";

import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"

import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { BaseComponent } from "./base.component";
@Component({
  selector: "modules-base-properties",
  templateUrl: "base-properties.component.html",
  styleUrls: ["base-properties.component.scss"],
})
export class BasePropertiesComponent extends BaseComponent implements OnInit {

  dataSource = null;
  displayedColumns = null;

  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _router: Router,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _router)
    this._name = 'BaseProperties';

  }

  ngOnInit() {
  }

  getData() {
    if(!this.value) {
      return of(null)
    }
    return this._mData.getOne(
      this.schemaName,
      this.value
    );
  }

  processData(data) {
    this.data = data
    this.dataSource = this.schemaConfig.utils.columns_array.map(
      p => ({
        name: p.name,
        label: p.label,
        type: p.type,
        value: this.data[p.name]
      })
    );
    this.displayedColumns = ['name', 'label', 'type', 'value']
    this.setLayersData(true);
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
