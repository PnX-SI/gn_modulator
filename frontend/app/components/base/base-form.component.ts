import { Component, OnInit } from "@angular/core";
import { of } from "@librairies/rxjs";

import { ModulesService } from "../../services/all.service";
import { WidgetLibraryService } from "@ajsf/core";

import { additionalWidgets } from "./form";
import utils from "../../utils";

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

  currentLayer;
  dataSave = null;

  drawOptions = null;
  // geometryFormGroup;
  processedLayout = {};
  additionalWidgets = additionalWidgets;

  constructor(
    _services: ModulesService,
    private _widgetLibraryService: WidgetLibraryService
  ) {
    super(_services);
    this.mapId = `base-form_${Math.random()}`;
    this._name = "BaseForm";
  }

  ngOnInit() {
    this._services.mapService.waitForMap(this.mapId).then(() => {
      this._services.mapService.getMap(this.mapId).on("pm:create", (event) => {
        if(this.currentLayer) {
          this._services.mapService.getMap(this.mapId).removeLayer(this.currentLayer);
        }
        this.currentLayer=event.layer;
        // remove previous layer if needed

        event.layer.on("pm:edit", ({ layer }) => {
          // layer has been edited
          this.setDataGeom(layer);
          this.setLayersData();
        });
        this.setDataGeom(event.layer);
        this.setLayersData();
      });

    });

    for (const [key, AdditionalWidget] of Object.entries(additionalWidgets)) {
      this._widgetLibraryService.registerWidget(key, AdditionalWidget);
    }
    setTimeout(() => {
      this.bDraw = true;
    }, 3000);
    this.initHeight();
  }

  setDataGeom(layer) {
    this.data[this.geometryFieldName()] = null;

    const dataGeom = layer.toGeoJSON().geometry;
    this.setSchemaGeom(dataGeom);
    this.data[this.geometryFieldName()] = dataGeom;
    this._services.mLayout.reComputeLayout();
  }

  setComponentTitle(): void {
    this.componentTitle = this.id()
      ? `Modification ${this.schemaConfig.display.du_label} ${this.label()}`
      : `Creation ${this.schemaConfig.display.un_nouveau_label}`;
  }

  processConfig(): void {
    this.layout = this.schemaConfig.form.layout;
    this.processedLayout = {
      type: "form",
      appearance: "fill",
      height_auto: true,
      // tester avant  set Layer ????
      change: () => {this.setLayersData(true)},
      items: [
        {
          title: [
            "__f__{",
            `  const id = data.${this.schemaConfig.utils.pk_field_name};`,
            "  return id",
            "    ? `Modification " +
              this.schemaConfig.display.du_label +
              " ${data." + this.schemaConfig.utils.label_field_name + "}`",
            `    : "Création + ${this.schemaConfig.display.un_nouveau_label}";`,
            "}",
          ],
        },
        {
          hidden: "__f__(data.geom && data.geom.coordinates)",
          type: "message",
          html: "<b>Veuillez saisir une geométrie sur la carte</b>",
          class: "warning",
          center: true
        },
        {
          type: "message",
          json: "__f__utils.getFormErrors(formGroup)",
          class: "warning",
          center: true,
          hidden: true
        },
        {
          items: this.schemaConfig.form.layout,
          overflow: true,
        },
        {
          direction: "row",

          items: [
            {
              flex: "initial",
              type: "button",
              color: "primary",
              title: "Valider",
              description: "Enregistrer le contenu du formulaire",
              action: "submit",
              disabled: "__f__!(formGroup.valid && data.geom && data.geom.coordinates )"
            },
            {
              flex: "initial",
              type: "button",
              color: "primary",
              title: "Annuler",
              description: "Annuler l'édition",
              action: "details",
            },
          ],
        },
      ],
    };
  }

  getDrawOptions() {
    const geometryType = this.geometryType();
    if (!geometryType) {
      return;
    }
    const drawOptions = {
      drawCircle: false,
      drawCircleMarker: false,
      drawRectangle: false,
      drawMarker: ["geometry", "point"].includes(geometryType),
      drawPolygon: ["geometry", "polygon"].includes(geometryType),
      drawPolyline: ["geometry", "polyline"].includes(geometryType),
      dragMode: geometryType != "point",
      cutPolygon: false,
      removalMode: false,
      rotateMode: false,
    };
    return drawOptions;
  }

  getFields() {
    const fields = this._services.mLayout.getLayoutFields(this.layout);

    if (this.hasGeometry) {
      fields.push(this.geometryFieldName());
    }

    if (!fields.includes(this.pkFieldName())) {
      fields.push(this.pkFieldName());
    }

    return fields;
  }

  getData() {
    if (!this.value) {
      return of({});
    }
    const fields = this.getFields();
    return this._services.mData.getOne(this.schemaName, this.value, {
      fields,
    });
  }

  processData(data) {
    this.setSchemaGeom(data[this.geometryFieldName()]);
    this.data = data;
    this.drawOptions = this.getDrawOptions();
    this.setLayersData(true);
  }

  /**
   * patch car oneOf ne marche pas pour les geometrie pff
   */
  setSchemaGeom(dataGeomField) {
    const schemaForm = this.schemaConfig.form.schema;
    const schemaGeomField = schemaForm.properties[this.geometryFieldName()];
    if (dataGeomField) {
      schemaGeomField.$ref = `#/definitions/references_geom_${dataGeomField.type.toLowerCase()}`;
    }
    // pour que le changement de schema soit pris en compte
    this.schemaConfig = utils.copy(this.schemaConfig);
  }

  onIsValid(event) {
    this.isValid = event;
  }

  onValidationErrors(event) {
    this.validationErrors = event;
  }

  onFormChanges(event) {
    if (
      !event ||
      JSON.stringify(event) === "{}" ||
      utils.fastDeepEqual(event, this.dataSave)
    ) {
      return;
    }

    this.dataSave = event;
    // test depuis la derniere json stringify ou autre
    this.data = event;

    // this.setLayersData(true);
  }

  setLayersData(flyToPoint = false) {
    const properties = {
      id: this.id(),
    };

    const geometry = this.data[this.geometryFieldName()];
    if (!(geometry && geometry.coordinates)) {
      this.data[this.geometryFieldName()] = {
        type: null,
        coordinates: null,
      };
      return;
    }
    if (flyToPoint) {
      this._services.mapService.waitForMap(this.mapId).then(() => {
        this._services.mapService.setCenter(this.mapId, geometry);
      });
    }
    this.layersData = {
      geomEdit: {
        geojson: {
          type: "Feature",
          geometry,
          properties,
        },
        layerOptions: {
          type: "marker",
          pkFieldName: this.pkFieldName(),
          onEachFeature: (feature, layer) => {
            layer.on("pm:edit", (event) => {
              this.setDataGeom(event.layer);
              // this.setLayersData();
              // set layer in data
              // set layer in layerData
            });
          },
        },
      },
    };
  }

  onAction(event) {
    if (event.action == "submit") {
      this.onSubmit(event.data);
    }
    if (event.action == "details") {
      this.emitEvent({
        action: "details",
        params: {
          value: this.id(),
        },
      });
    }
  }

  onSubmit(data) {
    if (!data) {
      return;
    }
    let request = null;
    const requestType = this.id() ? "patch" : "post";
    const fields = this.getFields();

    const processedData = this._services.mForm.processData(data, this.layout);

    if (this.id()) {
      request = this._services.mData.patch(
        this.schemaName,
        this.id(),
        processedData,
        {
          fields,
        }
      );
    } else {
      request = this._services.mData.post(this.schemaName, processedData, {
        fields,
      });
    }

    request.subscribe(
      (requestData) => {
        this.data = requestData;
        const prettyRequestType =
          requestType == "patch" ? "de modification" : "d'ajout";
        this._services.commonService.regularToaster(
          "success",
          `La requete ${requestType} pour l'object ${
            this.schemaName
          } d'id ${this.id()} a bien été effectué`
        );
        // redirect ??
        this.emitEvent({
          action: "details",
          params: {
            value: this.id(),
          },
        });
      },
      (error) => {
        this._services.commonService.regularToaster(
          "error",
          `Erreur dans la requete ${requestType} pour l'object ${
            this.schemaName
          } d'id ${this.id()}`
        );
      }
    );
  }

  onCancelClick() {
    this.emitEvent({
      action: "details",
      params: {
        value: this.id(),
      },
    });
  }
}
