import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { WidgetLibraryService } from 'angular7-json-schema-form';
import { ModulesConfigService } from "../../services/config.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesMapService } from "../../services/map.service"
import { ModulesFormService } from "../../services/form.service"
import { CommonService } from "@geonature_common/service/common.service";
import { ModulesRouteService } from "../../services/route.service"

import { additionalWidgets } from './form'
import utils from '../../utils';

import { BaseComponent } from "./base.component";
@Component({
  selector: "modules-base-form",
  templateUrl: "base-form.component.html",
  styleUrls: ["base.scss", "base-form.component.scss"],
})
export class BaseFormComponent extends BaseComponent implements OnInit {

  formTitle = null;
  validationErrors = null;
  isValid = null;
  bDraw = false;
  geometry = null;

  dataSave= null;

  drawOptions=null;
  geometryFormGroup;
  processedLayout = {};
  additionalWidgets = additionalWidgets;

  constructor(
    _route: ActivatedRoute,
    _commonService: CommonService,
    _mapService: ModulesMapService,
    _mConfig: ModulesConfigService,
    _mData: ModulesDataService,
    _mForm: ModulesFormService,
    _router: Router,
    _mRoute: ModulesRouteService,
    private _widgetLibraryService: WidgetLibraryService,
    private _formBuilder: FormBuilder,
  ) {
    super(_route, _commonService, _mapService, _mConfig, _mData, _mForm, _router, _mRoute)
    this.mapId = `base-form_${Math.random()}`;
    this._name = 'BaseForm';

  }

;

  ngOnInit() {
    // charge les widget additionels
    this.geometryFormGroup=this._formBuilder.group({'geometry': [null, Validators.required]})
    for (const [key, AdditionalWidget] of Object.entries(additionalWidgets)) {
      this._widgetLibraryService.registerWidget(key, AdditionalWidget);
    }
    setTimeout(() => {this.bDraw = true}, 3000)
    this.setFullHeight();
  }

  setComponentTitle(): void {
    this.componentTitle = this.id()
      ? `Modification ${this.schemaConfig.display.prep_label} ${this.id()}`
      : `Creation ${this.schemaConfig.display.undef_label_new}`
    ;
  }

  processConfig(): void {
      this.layout = this.schemaConfig.form.layout
      this.processedLayout = this._mForm.processLayout(this.layout);
      console.log(this.processedLayout);
      if(Array.isArray(this.processedLayout)) {
        this.processedLayout.push({
          type: 'submit',
          classHtml: 'hidden form-submit-button'
        })
      }
  }

  getDrawOptions() {
    const geometryType = this.geometryType();
    if (!geometryType) {
      return
    }
    const drawOptions = {
      drawCircle: false,
      drawCircleMarker: false,
      drawRectangle: false,
      drawMarker: !this.id() && ['geometry', 'point'].includes(geometryType),
      drawPolygon: !this.id() && ['geometry', 'polygon'].includes(geometryType),
      drawPolyline: !this.id() && ['geometry', 'polyline'].includes(geometryType),
      dragMode: geometryType != 'point',
      cutPolygon: false,
      removalMode: false,
      rotateMode: false,
    }
    return drawOptions;
  }

  getFields() {
    const fields = this.getLayoutFields(this.layout, true)
    if (this.hasGeometry) {
      fields.push(this.geometryFieldName());
    }

    if(!fields.includes(this.pkFieldName())) {
      fields.push(this.pkFieldName());
    }
    return fields;
  }

  getData() {

    const fields = this.getFields()

    if(!this.value) {
      return of(null)
    }
    return this._mData.getOne(
      this.schemaName,
      this.value,
      {
        fields
      }
    );
  }

  processData(data) {
    this.data = data;
    this.drawOptions = this.getDrawOptions();
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

  onSubmit($event) {
    let request = null;
    const requestType = this.id()
      ? 'patch'
      : 'post'
    ;

    const fields = this.getFields();

    if (this.id()) {
        request = this._mData.patch(this.schemaName, this.id(), this.data, { fields })
    } else {
        request = this._mData.post(this.schemaName, this.data, { fields })
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
        // redirect ??
        this.emitEvent({
          action: 'details',
          params: {
            value: this.id()
          }
        })
      },
      (error) => {
        this._commonService.regularToaster(
          "error",
          `Erreur dans la requete ${requestType} pour l'object ${this.schemaName} d'id ${this.id()} a bien été effectué`
        );

      });
  }

  onSubmitClick() {
    // const elems = document.getElementsByClassName('form-submit-button');
    // elems[0].click();
    this.onSubmit(null);
  }

  onCancelClick() {
    this.emitEvent({
      action: 'details',
      params: {
        value: this.id()
      }
    });
  }

}

