import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";

import { ModulesConfigService } from "../../services/config.service";
import { ModulesDataService } from "../../services/data.service";
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"
import { AuthService } from "@geonature/components/auth/auth.service";

import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
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
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _mForm: ModulesFormService,
    _router: Router,
    _mRoute: ModulesRouteService,
    _auth: AuthService,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute, _auth)
    this._name = 'BaseProperties';

  }

  ngOnInit() {
    this.initHeight()
  }

  getData() {
    if(!this.value) {
      return of(null)
    }

    const fields = this.getLayoutFields(this.layout, true)

    if(!fields.includes(this.pkFieldName())) {
      fields.push(this.pkFieldName());
    }

    if (this.hasGeometry() && !fields.includes(this.geometryFieldName())) {
      fields.push(this.geometryFieldName());
    }

    fields.push('cruved_ownership')

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
    this.bEditAllowed = data['cruved_ownership'] <= this.moduleConfig.cruved['U'];
    for (const field of this.getLayoutFields(this.layout)) {
      var key = field.key || field;
      var keyValue = field.key_value || field.key || field;
      var keyProp = keyValue.split('.')[0];
      const property = this.schemaConfig.schema.properties[keyProp];
      var title = field.title || property.title;
      const value =
        field.filters
          ? utils.getAttr(utils.filtersAttr(this.data, field.filters), keyValue)
          : utils.getAttr(this.data, keyValue)
      this.layoutData[key] = {
        title,
        value
      }
    }
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

  onEditClick() {
    this.emitEvent({
      action: 'edit',
      params: {
        value: this.id()
      }
    });
  }

}
