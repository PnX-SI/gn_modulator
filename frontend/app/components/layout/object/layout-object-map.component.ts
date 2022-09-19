import { Component, OnInit, Injector } from "@angular/core";
import { ModulesMapService } from "../../../services/map.service";
import { ModulesLayoutObjectComponent } from "./layout-object.component";
import { Observable } from "@librairies/rxjs";
import utils from "../../../utils";

@Component({
  selector: "modules-layout-object-map",
  templateUrl: "layout-object-map.component.html",
  styleUrls: ["../../base/base.scss", "layout-object-map.component.scss"],
})
export class ModulesLayoutObjectMapComponent
  extends ModulesLayoutObjectComponent
  implements OnInit
{
  mapId;
  zoom;
  center;
  layersData;
  _mapService;

  mapData;
  height;

  tooltipDisplayZoomTreshold = 12;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-object-map";
    this.mapId = `map_${this._id}`;
    this._mapService = this._injector.get(ModulesMapService);
  }

  processConfig() {
    this.processedLayout = {
      type: "map",
      map_id: this.mapId,
    };
  }

  processValue(value) {
    if (!value) {
      //close popUp ???
      return;
    }

    if (this.isProcessing) {
      return;
    }

    const layerSearcghFilters = {};
    layerSearcghFilters[this.pkFieldName()] = value;
    if(!this.pkFieldName()) {
      return;
    }
    const layer = this._mapService.findLayer(this.mapId, layerSearcghFilters);
    if (!layer) {
      console.error(
        `le layer (${this.pkFieldName()}==${value}) n'est pas présent`
      );
      return;
    }
    layer.openPopup();
  }

  processFilters() {
    console.log('process filters')
    return this.processObject();
  }

  processData(response) {
    this.schemaData = response.data;
    this._mapService.waitForMap(this.mapId).then(() => {
      // this.schemaData = response.data;
      let geojson = response.data;
      const label_field_name = this.schemaConfig.utils.label_field_name;
      const pk_field_name = this.schemaConfig.utils.pk_field_name;
      const currentZoom = this._mapService.getZoom(this.mapId);
      const currentMapBounds = this._mapService.getMapBounds(this.mapId);
      // this.mapData = {};
      this.mapData = {
        pf: {
          geojson,
          layerOptions: {
            key: "pf",
            label: `${this.schemaConfig.display.labels}`,
            bZoom: true,
            onLayersAdded: () => {
              this.processValue(this.getDataValue());
            },
            onEachFeature: (feature, layer) => {
              /** click */
              layer.on("click", (event) => {
                const value = event.target.feature.properties[pk_field_name];
                this.setObject({ value });
              });

              /** tooltip */
              const label = feature.properties[label_field_name];
              if (label) {
                const action =
                  this._mapService.actionTooltipDisplayZoomThreshold(
                    this.mapId,
                    layer,
                    this.tooltipDisplayZoomTreshold,
                    false,
                    currentZoom,
                    currentMapBounds
                  );
                layer
                  .bindTooltip(label, {
                    direction: "top",
                    permanent: action == "display",
                    className: "anim-tooltip",
                  })
                  .openTooltip();

                /** tooltip - zoom et emprise */
                layer.onZoomMoveEnd = this._mapService.layerZoomMoveEndListener(
                  this.mapId,
                  layer,
                  this.tooltipDisplayZoomTreshold
                );
              }
              layer
                .bindPopup(this.popupHTML(feature.properties))
                .on("popupopen", (event) => {
                  this.onPopupOpen(layer);
                });
            },
          },
        },
      };
    });
  }

  popupHTML(properties) {
    const label = properties[this.labelFieldName()];
    const popupFields = this.schemaConfig.map.popup_fields || [];
    var propertiesHTML = "";
    propertiesHTML += "<ul>\n";
    propertiesHTML += popupFields
      .filter((fieldKey) => fieldKey != "cruved_ownership")
      .map((fieldKey) => {
        // gerer les '.'
        const fieldKeyLabel = fieldKey.split(".")[0];
        const fieldLabel =
          this.schemaConfig.definition.properties[fieldKeyLabel].title;
        const fieldValue = utils.getAttr(properties, fieldKey);
        return `<li>${fieldLabel} : ${fieldValue}</li>`;
      })
      .join("\n");
    propertiesHTML += "</ul>\n";

    const htmlDetails = '<button action="details">Details</button>';
    const condEdit =
      properties["cruved_ownership"] <= this.moduleConfig.module.cruved["U"];
    const htmlEdit = condEdit ? '<button action="edit">Éditer</button>' : "";

    const html = `
    <h4>${label || ""}</h4>
    <div>
      ${htmlDetails}
      ${htmlEdit}
    </div>
    ${propertiesHTML}
    `;
    return html;
  }

  onPopupOpen(layer) {
    const value = layer.feature.properties[this.pkFieldName()];
    // const fields = this.schemaConfig.table.columns.map(column => column.field);
    const fields = this.schemaConfig.map.popup_fields;
    // if(this.schemaConfig.definition.meta.check_cruved) {
    fields.push("cruved_ownership");
    // }
    this._mData
      .getOne(this.schemaName(), value, { fields })
      .subscribe((data) => {
        layer.setPopupContent(this.popupHTML(data));
      });
    this._mapService.L.DomEvent.on(
      layer.getPopup().getElement(),
      "click",
      (e) => {
        const action =
          e && e.target && e.target.attributes.getNamedItem("action").nodeValue;
        if (action) {
          this._mPage.processAction({
            action,
            objectName: this.objectName(),
            value,
          });
        }
      }
    );
  }

  getData(): Observable<any> {
    const extendedParams = {
      fields: [
        this.schemaConfig.utils.pk_field_name,
        this.schemaConfig.utils.label_field_name,
      ], // fields
      filters: this.getDataFilters() || [],
      as_geojson: true,
    };
    return this._mData.getList(this.schemaName(), extendedParams);
  }
}
