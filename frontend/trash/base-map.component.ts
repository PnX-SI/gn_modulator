import { Component, OnInit, Input, SimpleChanges, } from "@angular/core";
import { ModulesService } from "../../services/all.service";

import { BaseComponent } from "./base.component";
import utils from '../../utils'
@Component({
  selector: "modules-base-map",
  templateUrl: "base-map.component.html",
  styleUrls: [ "base.scss", "base-map.component.scss", ],
})
export class BaseMapComponent extends BaseComponent implements OnInit {

  @Input() compress = null;

  // @Output() onLayerClick: EventEmitter<any> = new EventEmitter<any>();

  mapTitle = null;

  page_size = 0;

  tooltipDisplayZoomTreshold=12;

    constructor(
      _services: ModulesService
    ) {
      super(_services)
      this._name = 'BaseMap'
    }

  ngOnInit() {
    this.initHeight()
  }

  getData() {
    if(this.compress) {
      const extendedParams = {
        fields: [
          this.schemaConfig.utils.pk_field_name,
          this.schemaConfig.utils.label_field_name,
          this.schemaConfig.utils.geometry_field_name
        ], // fields
        filters: this.filters,
        compress: true,
        page_size: this.page_size
      };
      return this._services.mData.getList(this.schemaName, extendedParams)
    } else {
      const extendedParams = {
        fields: [this.schemaConfig.utils.pk_field_name, this.schemaConfig.utils.label_field_name], // fields
        filters: this.filters,
        as_geojson: true,
      };
      return this._services.mData.getList(this.schemaName, extendedParams)
    }
  }

  processValue(value) {
    if (!value) {
      //close popUp ???
      return;
    }

    const layerSearcghFilters = {};
    layerSearcghFilters[this.pkFieldName()] = value;
    const layer = this._services.mapService.findLayer(this.mapId, layerSearcghFilters)
    if (! layer) {
      console.error(`le layer (${this.pkFieldName()}==${value}) n'est pas présent`)
      return;
    }
    layer.openPopup();
  };

  onPopupOpen(layer) {
    const value = layer.feature.properties[this.pkFieldName()];
    // const fields = this.schemaConfig.table.columns.map(column => column.field);
    const fields = this.schemaConfig.map.popup_fields;
    // if(this.schemaConfig.definition.meta.check_cruved) {
      fields.push('ownership');
    // }
    this._services.mData.getOne(this.schemaName, value, { fields })
    .subscribe((data) => {
      layer.setPopupContent(this.popupHTML(data));
    });
    this._services.mapService.L.DomEvent
    .on(layer.getPopup().getElement(), 'click', (e) => {
      const action =  e && e.target && e.target.attributes.getNamedItem('action').nodeValue;
      if(action) {
        const event = {
          action: action,
          params: {
            value
          },
          component: this._name
        }
        this.emitEvent(event);
      }
    });

  }

  processData(response) {
    this.data = response.data;
    let geojson = response.data;
    if(this.compress) {

      geojson = this.data.map((d) => {
        const properties = {};
        for (const [index, f] of Object.entries(d)) {
          properties[response['fields'][index]] = f;
        }
        return {
          type: 'Feature',
          geometry: {
              type: 'Point',
              coordinates: [properties['x'], properties['y']],
          },
          properties
        }
      });
    }

    const label_field_name = this.schemaConfig.utils.label_field_name;
    const pk_field_name = this.schemaConfig.utils.pk_field_name;
    const currentZoom = this._services.mapService.getZoom(this.mapId)
    const currentMapBounds = this._services.mapService.getMapBounds(this.mapId)

    this.layersData = {
      pf: {
        geojson,
        layerOptions: {
          label: `${this.schemaConfig.display.labels}`,
          bZoom: true,
          onEachFeature: (feature, layer) => {

            /** click */
            layer.on('click', (event) => {
              const value = event.target.feature.properties[pk_field_name];
              // this.onLayerClick.emit({value});
              this.emitEvent({
                action: 'selected',
                params: {
                  value
                }
              });
            });

            /** tooltip */
            const label = feature.properties[label_field_name];
            if(label) {
              const action = this._services.mapService.actionTooltipDisplayZoomThreshold(
                this.mapId,
                layer,
                this.tooltipDisplayZoomTreshold,
                false,
                currentZoom,
                currentMapBounds,
              );
              layer.bindTooltip(
                label,
                {
                  direction: 'top',
                  permanent: action == 'display',
                  className: 'anim-tooltip'
                }
              ).openTooltip();

            /** tooltip - zoom et emprise */
              layer.onZoomMoveEnd = this._services.mapService
                .layerZoomMoveEndListener(this.mapId, layer, this.tooltipDisplayZoomTreshold)
            }
            layer.bindPopup(this.popupHTML(feature.properties))
              .on('popupopen', (event) => {
                this.onPopupOpen(layer);
              });
          }
        }
      }
    }
  }

  popupHTML(properties) {
    const label = properties[this.labelFieldName()];
    const popupFields = this.schemaConfig.map.popup_fields || [];
    var propertiesHTML="";
    propertiesHTML += '<ul>\n'
    propertiesHTML += popupFields
      .filter(fieldKey => fieldKey != "ownership")
      .map( fieldKey => {
        // gerer les '.'
        const fieldKeyLabel = fieldKey.split('.')[0]
        const fieldLabel = this.schemaConfig.definition.properties[fieldKeyLabel].title;
        const fieldValue = utils.getAttr(properties, fieldKey)
        return `<li>${fieldLabel} : ${fieldValue}</li>`
      })
      .join('\n');
    propertiesHTML += '</ul>\n'

    const htmlDetails = '<button action="details">Details</button>'
    const condEdit = properties['ownership'] <= this.moduleConfig.module.cruved['U'];
    const htmlEdit = condEdit
      ? '<button action="edit">Éditer</button>'
      : '';

    const html = `
    <h4>${label || ''}</h4>
    <div>
      ${htmlDetails}
      ${htmlEdit}
    </div>
    ${propertiesHTML}
    `
    return html;
  }

  setMapTitle() {
      this.mapTitle = `Carte ${this.schemaConfig.display.des_labels}`;
  }

  // getZoom() {
  //   return this._services.mapService.getZoom(this.mapId)
  // }

  ngOnChanges(changes: SimpleChanges) {
    for (const [key, change] of Object.entries(changes)) {
      if(
        ['schemaName', 'filters'].includes(key)
      ) {
        this.process();
      }
      if(key == 'value') {
        // TODO
          this.processValue(this.value)
      }
    }
  }

}

