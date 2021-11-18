import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { HttpClient } from "@angular/common/http";
import { WidgetLibraryService } from 'angular7-json-schema-form';
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesMapService } from "../../services/map.service"
import { CommonService } from "@geonature_common/service/common.service";

import { additionalWidgets } from './form'
import utils from '../../utils';

import { BaseComponent } from "./base.component";
@Component({
  selector: "modules-base-form",
  templateUrl: "base-form.component.html",
  styleUrls: ["base-form.component.scss"],
})
export class BaseFormComponent extends BaseComponent implements OnInit {

  formTitle = null;
  validationErrors = null;
  isValid = null;
  bDraw = false;
  geometry = null;

  dataSave= null;

  geometryFormGroup;

  additionalWidgets = additionalWidgets;

  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _router: Router,
    private _widgetLibraryService: WidgetLibraryService,
    private _formBuilder: FormBuilder,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _router)
    this.mapId = 'base-form';
    this._name = 'BaseForm';

  }


  ngOnInit() {
    // charge les widget additionels
    this.geometryFormGroup=this._formBuilder.group({'geometry': [null, Validators.required]})
    for (const [key, AdditionalWidget] of Object.entries(additionalWidgets)) {
      this._widgetLibraryService.registerWidget(key, AdditionalWidget);
    }
    setTimeout(() => {this.bDraw = true}, 3000)
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
    this.formTitle = this.id()
      ? `Modification ${this.schemaConfig.display.prep_label} ${this.id()}`
      : `Creation ${this.schemaConfig.display.undef_label_new}`
    ;
    this.setLayersData(true);
  }

  onIsValid(event) {
    this.isValid=event;
  }

  onValidationErrors(event) {
    this.validationErrors=event
  }

  onFormChanges(event) {
    if((!event) || JSON.stringify(event) === '{}' || utils.fastDeepEqual(event, this.dataSave)) {
      return
    }
    this.dataSave  = event;
    // test depuis la derniere json stringify ou autre
    this.data = event;
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
          pkFieldName: this.pkFieldName(),
          onEachFeature: (feature, layer) => {
            layer.on('pm:edit', (event) => {
              this.data[this.geometryFieldName()] = event.layer.toGeoJSON().geometry;
              this.setLayersData();
              // set layer in data
              // set layer in layerData
            })
          }
        }
      }
    }
  }

  // onLayerDrawChanged(event) {
  //   this.data[this.schemaConfig.utils.geometry_field_name] = event.geometry;
  // };
  // onGPSChanged(event) {};
  // onFileLayerChanged(event) {};

  onSubmit($event) {
    let request = null;
    const requestType = this.id()
      ? 'patch'
      : 'post'
    ;

    if (this.id()) {
        request = this._mData.patch(this.schemaName, this.id(), this.data)
    } else {
        request = this._mData.post(this.schemaName, this.data)
    }

    request.subscribe(
      (data) => {
        this.data=data;
        const prettyRequestType = requestType == 'patch'
          ? 'de modification'
          : "d'ajout"
        ;
        this._commonService.regularToaster(
          "success",
          `La requete ${requestType} pour l'object ${this.schemaName} d'id ${this.id()} a bien été effectué`
        );

      },
      (error) => {
        this._commonService.regularToaster(
          "error",
          `Erreur dans la requete ${requestType} pour l'object ${this.schemaName} d'id ${this.id()} a bien été effectué`
        );

      });
  }
}

