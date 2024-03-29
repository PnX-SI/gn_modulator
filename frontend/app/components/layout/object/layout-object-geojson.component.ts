import { Component, OnInit, Injector } from '@angular/core';
import { ModulesMapService } from '../../../services/map.service';
import { ModulesLayoutObjectComponent } from './layout-object.component';
import { Observable, of } from '@librairies/rxjs';
import utils from '../../../utils';

@Component({
  selector: 'modules-layout-object-geojson',
  templateUrl: 'layout-object-geojson.component.html',
  styleUrls: ['../../base/base.scss', 'layout-object-geojson.component.scss'],
})
export class ModulesLayoutObjectGeoJSONComponent
  extends ModulesLayoutObjectComponent
  implements OnInit
{
  zoom;
  center;
  layersData;
  _mapService;

  mapData;
  height;

  tooltipDisplayZoomTreshold = 12;

  removedByZoom = false;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-object-geojson';
    this._mapService = this._injector.get(ModulesMapService);
  }

  processConfig() {}

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
    if (!this.pkFieldName()) {
      return;
    }
    const layer = this._mapService.findLayer(this.context.map_id, layerSearcghFilters);
    if (!layer) {
      return;
    }

    layer.bringToFront();
    this.computedLayout.open_popup && layer.openPopup();
  }

  processFilters() {
    return this.processObject();
  }

  processPreFilters() {
    return this.processObject();
  }

  processData(response) {
    const pk_field_name = this.objectConfig().utils.pk_field_name;

    if (!response.data) {
      return;
    }

    this.objectData = response.data;
    this._mapService.waitForMap(this.context.map_id).then(() => {
      let geojson = response.data;
      const label_field_name = this.objectConfig().utils.label_field_name;
      const currentZoom = this._mapService.getZoom(this.context.map_id);
      const currentMapBounds = this._mapService.getMapBounds(this.context.map_id);

      const layerStyle =
        this.computedLayout.style || this.objectConfig()?.map?.style || this.context.map?.style;
      const bZoom = this.computedLayout.zoom || this.context.map?.zoom;
      const bTooltipPermanent = this.computedLayout.tooltip_permanent;
      const bring_to_front = this.computedLayout.bring_to_front || this.context.map?.bring_to_front;
      this.mapData = {
        geojson,
        layerOptions: {
          bring_to_front,
          zoom: bZoom,
          key: this.computedLayout.key,
          deflate: this.computedLayout.deflate,
          activate: this.computedLayout.activate,
          pk_field_name,
          title: utils.capitalize(this.computedLayout.title || this.objectConfig().display.labels),
          style: layerStyle,
          onLayersAdded: () => {
            this.processValue(this.getDataValue());
            this._mapService.setProcessing(this.context.map_id, false);
          },
          onEachFeature: (feature, layer) => {
            /** click */
            layer.on('click', (event) => {
              const value = event.target.feature.properties[pk_field_name];
              this.setObject({ value });
            });

            /** tooltip */
            const label = utils.getAttr(feature.properties, label_field_name);
            if (label) {
              const action = this._mapService.actionTooltipDisplayZoomThreshold(
                this.context.map_id,
                layer,
                this.tooltipDisplayZoomTreshold,
                false,
                currentZoom,
                currentMapBounds,
              );
              layer
                .bindTooltip(label.toString(), {
                  direction: 'top',
                  permanent: action == 'display' && bTooltipPermanent,
                  className: 'anim-tooltip',
                })
                .openTooltip();

              /** tooltip - zoom et emprise */
              if (bTooltipPermanent) {
                layer.onZoomMoveEnd = this._mapService.layerZoomMoveEndListener(
                  this.context.map_id,
                  layer,
                  this.tooltipDisplayZoomTreshold,
                );
              }
            }
            layer.bindPopup(this.popupHTML(feature.properties)).on('popupopen', (event) => {
              this.onPopupOpen(layer);
            });
          },
        },
      };
      const d = {};
      d[this.context.object_code] = this.mapData;
      this._mapService.processData(this.context.map_id, d, {
        zoom: this.computedLayout.zoom,
      });
    });
  }

  popupHTML(properties) {
    const fields = this.popupFields();
    const label = `<b>${this.utils.capitalize(
      this.objectConfig().display.label,
    )}</b>: ${utils.getAttr(properties, this.labelFieldName())}`;
    var propertiesHTML = '';
    propertiesHTML += '<ul>\n';
    propertiesHTML += fields
      .filter((field) => field != 'scope')
      .map((field) => {
        let fieldLabel, fieldKey;
        if (utils.isObject(field)) {
          fieldKey = field.key;
          fieldLabel = field.title;
        } else {
          fieldKey = field;
        }
        if (!fieldLabel) {
          const fieldKeyLabel = fieldKey.split('.')[0];
          fieldLabel = this.objectConfig().properties[fieldKeyLabel].title || fieldKey;
        }
        const fieldValue = utils.getAttr(properties, fieldKey);
        return `<li>${fieldLabel} : ${fieldValue}</li>`;
      })
      .join('\n');
    propertiesHTML += '</ul>\n';

    const htmlDetails = this._mObject.checkAction(this.context, 'R', properties.scope).actionAllowed
      ? '<button action="details">Détails</button>'
      : '';
    const htmlEdit = this._mObject.checkAction(this.context, 'U', properties.scope).actionAllowed
      ? '<button action="edit">Éditer</button>'
      : '';

    const htmlDelete = '';
    // const htmlDelete = this._mObject.checkAction(this.context, 'D', properties.scope).actionAllowed
    //   ? '<button action="delete">Supprimer</button>'
    //   : '';

    const html = `
    <h4>${label || ''}</h4>
    <div>
      ${htmlDetails}
      ${htmlEdit}
      ${htmlDelete}
    </div>
    ${propertiesHTML}
    `;

    return html;
  }

  popupFields(): Array<any> {
    return this.computedLayout.popup_fields || this.defaultFields();
  }

  onPopupOpen(layer) {
    const value = layer.feature.properties[this.pkFieldName()];
    const fields = this.popupFields().map((f) => f.key || f);
    fields.push('scope');
    layer.setPopupContent('chargement ...');
    this._mData
      .getOne(this.moduleCode(), this.objectCode(), value, { fields })
      .subscribe((data) => {
        layer.setPopupContent(this.popupHTML(data));
      });
    this._mapService.L.DomEvent.on(layer.getPopup().getElement(), 'click', (e) => {
      const action = e && e.target && e.target.attributes.getNamedItem('action')?.nodeValue;
      if (action) {
        this._mAction.processAction({
          action,
          context: this.context,
          value,
        });
      }
    });
  }

  getData(): Observable<any> {
    // test Zoom min
    const key = this.context.object_code;
    const currentLayer = this._mapService.getLayerData(
      this.context.map_id,
      this.context.object_code,
    );

    const condZoom =
      !this.computedLayout.zoom_min ||
      this._mapService.getZoom(this.context.map_id) >= this.computedLayout.zoom_min;

    if (this.removedByZoom && condZoom) {
      this.removedByZoom = false;
      this._mapService.showLayers(this.context.map_id, { key });
    }

    if (currentLayer && !this.removedByZoom && !condZoom) {
      this.removedByZoom = true;
      this._mapService.hideLayers(this.context.map_id, { key });
    }

    if (!condZoom) {
      return of({});
    }

    if (this.getDataPreFilters()?.includes('undefined')) {
      console.error('prefilter inconnu');
      return of({});
    }
    this._mapService.setProcessing(this.context.map_id, true);
    const extendedParams = {
      fields: this.fields({ geometry: true }), // fields
      filters: this.getDataFilters() || [],
      prefilters: this.getDataPreFilters() || [],
      as_geojson: true,
    };
    return this._mData.getList(this.moduleCode(), this.objectCode(), extendedParams);
  }
  refreshData(objectCode: any): void {
    if (objectCode == this.context.object_code) {
      this.postProcessLayout();
    }
  }
}
