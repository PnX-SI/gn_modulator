import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter } from "@angular/core";
import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { ModulesConfigService } from "../../services/config.service"
import { ModulesMapService } from "../../services/map.service"
import { ModulesDataService } from "../../services/data.service"
import { ModulesFormService } from "../../services/form.service"
import { ModulesRouteService } from "../../services/route.service"

import { CommonService } from "@geonature_common/service/common.service";
import { mergeMap, concatMap } from "@librairies/rxjs/operators";
import { Observable, of, forkJoin } from "@librairies/rxjs";
import { BaseComponent } from "./base.component";

@Component({
  selector: "modules-base-map",
  templateUrl: "base-map.component.html",
  styleUrls: [ "base.scss", "base-map.component.scss", ],
})
export class BaseMapComponent extends BaseComponent implements OnInit {

  @Input() compress = null;

  // @Output() onLayerClick: EventEmitter<any> = new EventEmitter<any>();

  mapTitle = null;

  size = 0;

  tooltipDisplayZoomTreshold=12;

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
      this._name = 'BaseMap'
    }

  ngOnInit() {

  }

  getData() {
    if(this.compress) {
      const fields = this.schemaConfig.table.columns.map(column => column.field);
      const extendedParams = {
        fields: [
          this.schemaConfig.utils.pk_field_name,
          this.schemaConfig.utils.label_field_name,
          this.schemaConfig.utils.geometry_field_name
        ], // fields
        filters: this.filters,
        compress: true,
        size: this.size
      };
      return this._mData.getList(this.schemaName, extendedParams)
    } else {
      const fields = this.schemaConfig.table.columns.map(column => column.field);
      const extendedParams = {
        fields: [this.schemaConfig.utils.pk_field_name, this.schemaConfig.utils.label_field_name], // fields
        filters: this.filters,
        as_geojson: true,
      };
      return this._mData.getList(this.schemaName, extendedParams)
    }
  }

  processValue(value) {
    if (!value) {
      //close popUp ???
      return;
    }

    const layerSearcghFilters = {};
    layerSearcghFilters[this.pkFieldName()] = value;
    const layer = this._mapService.findLayer(this.mapId, layerSearcghFilters)
    if (! layer) {
      console.error(`le layer (${this.pkFieldName()}==${value}) n'est pas présent`)
      return;
    }
    layer.openPopup();
  };

  onPopupOpen(layer) {
    const value = layer.feature.properties[this.pkFieldName()];
    this._mData.getOne(this.schemaName, value)
    .subscribe((data) => {
      layer.setPopupContent(this.popupHTML(data));
    });
    this._mapService.L.DomEvent
    .on(layer.getPopup().getElement(), 'click', (e) => {
      const action =  e && e.target && e.target.attributes.getNamedItem('action').nodeValue;
      if(action) {
        this.setQueryParams({
          tab: action,
          value: value
        })
      }
    });

  }

  processData(response) {
    this.data = response.data;
    if(this.compress) {

      const geojson = this.data.map((d) => {
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

      const label_field_name = this.schemaConfig.utils.label_field_name;
      const pk_field_name = this.schemaConfig.utils.pk_field_name;
      const currentZoom = this._mapService.getZoom(this.mapId)
      const currentMapBounds = this._mapService.getMapBounds(this.mapId)

      this.layersData = {
        pf: {
          geojson,
          layerOptions: {
            label: `${this.schemaConfig.display.labels}`,
            bZoom: false,
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
                const action = this._mapService.actionTooltipDisplayZoomThreshold(
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
              layer.onZoomMoveEnd = this._mapService
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
    } else {
      this.data = response['data'];
      this.layersData = response['data'];
    }
  }

  popupHTML(properties) {
    const label = properties[this.labelFieldName()];
    const popupFields = this.schemaConfig.map.popup_fields ;
    var propertiesHTML="";
    propertiesHTML += '<ul>\n'
    propertiesHTML += popupFields
      .map( fieldKey => {
        const fieldLabel = this.schemaConfig.schema.properties[fieldKey].label;
        const fieldValue = properties[fieldKey]
        return `<li>${fieldLabel} : ${fieldValue}</li>`
      })
      .join('\n');
    propertiesHTML += '</ul>\n'

    const html = `
    <h4>${label || ''}</h4>
    <div>
      <button action="detail">Detail</button>
      <button action="edit">Edition</button>
    </div>
    ${propertiesHTML}
    `
    return html;
  }

  setMapTitle() {
      this.mapTitle = `Carte ${this.schemaConfig.display.undef_labels}`;
  }

  // getZoom() {
  //   return this._mapService.getZoom(this.mapId)
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

