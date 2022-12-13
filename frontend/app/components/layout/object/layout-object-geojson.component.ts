import { Component, OnInit, Injector } from '@angular/core';
import { ModulesMapService } from '../../../services/map.service';
import { ModulesLayoutObjectComponent } from './layout-object.component';
import { Observable } from '@librairies/rxjs';
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
      console.error(`le layer (${this.pkFieldName()}==${value}) n'est pas présent`);
      return;
    }
    layer.bringToFront();
    layer.openPopup();
  }

  processFilters() {
    return this.processObject();
  }

  processPreFilters() {
    return this.processObject();
  }

  processData(response) {
    this.objectData = response.data;
    this._mapService.waitForMap(this.context.map_id).then(() => {
      let geojson = response.data;
      const label_field_name = this.objectConfig().utils.label_field_name;
      const pk_field_name = this.objectConfig().utils.pk_field_name;
      const currentZoom = this._mapService.getZoom(this.context.map_id);
      const currentMapBounds = this._mapService.getMapBounds(this.context.map_id);

      const layerStyle = this.computedLayout.style || this.data.map?.style;
      const paneName = this.computedLayout.pane || this.data.map?.pane || `P1`;
      const bZoom = this.computedLayout.zoom || this.data.map?.zoom;

      const bring_to_front = this.computedLayout.bring_to_front || this.data.map?.bring_to_front;
      this.mapData = {
        geojson,
        layerOptions: {
          bring_to_front,
          pane: paneName,
          zoom: bZoom,
          key: this.computedLayout.key,
          label: `${this.objectConfig().display.labels}`,
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
            const label = feature.properties[label_field_name];
            if (label) {
              const action = this._mapService.actionTooltipDisplayZoomThreshold(
                this.context.map_id,
                layer,
                this.tooltipDisplayZoomTreshold,
                false,
                currentZoom,
                currentMapBounds
              );
              layer
                .bindTooltip(label, {
                  direction: 'top',
                  permanent: action == 'display',
                  className: 'anim-tooltip',
                })
                .openTooltip();

              /** tooltip - zoom et emprise */
              layer.onZoomMoveEnd = this._mapService.layerZoomMoveEndListener(
                this.context.map_id,
                layer,
                this.tooltipDisplayZoomTreshold
              );
            }
            layer.bindPopup(this.popupHTML(feature.properties)).on('popupopen', (event) => {
              this.onPopupOpen(layer);
            });
          },
        },
      };
      const d = {};
      d[this.computedLayout.key] = this.mapData;
      this._mapService.processData(this.context.map_id, d, {
        // key: this.computedLayout.key,
        zoom: this.computedLayout.zoom,
      });
    });
  }

  popupHTML(properties) {
    const label = `<b>${this.utils.capitalize(this.objectConfig().display.label)}</b>: ${
      properties[this.labelFieldName()]
    }`;
    const popupFields = this.objectConfig().map.popup_fields || [];
    var propertiesHTML = '';
    propertiesHTML += '<ul>\n';
    propertiesHTML += popupFields
      .filter((fieldKey) => fieldKey != 'ownership')
      .map((fieldKey) => {
        // gerer les '.'
        const fieldKeyLabel = fieldKey.split('.')[0];
        const fieldLabel = this.objectConfig().properties[fieldKeyLabel].title;
        const fieldValue = utils.getAttr(properties, fieldKey);
        return `<li>${fieldLabel} : ${fieldValue}</li>`;
      })
      .join('\n');
    propertiesHTML += '</ul>\n';

    const htmlDetails = '<button action="details">Details</button>';
    const condEdit = properties['ownership'] <= this.moduleConfig().cruved['U'];
    const htmlEdit = condEdit ? '<button action="edit">Éditer</button>' : '';

    const html = `
    <h4>${label || ''}</h4>
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
    const fields = this.objectConfig().map.popup_fields;
    fields.push('ownership');
    this._mData
      .getOne(this.moduleCode(), this.objectCode(), value, { fields })
      .subscribe((data) => {
        layer.setPopupContent(this.popupHTML(data));
      });
    this._mapService.L.DomEvent.on(layer.getPopup().getElement(), 'click', (e) => {
      const action = e && e.target && e.target.attributes.getNamedItem('action')?.nodeValue;
      if (action) {
        this._mPage.processAction({
          action,
          objectCode: this.objectCode(),
          value,
        });
      }
    });
  }

  getData(): Observable<any> {
    this._mapService.setProcessing(this.context.map_id, true);
    const extendedParams = {
      fields: [this.objectConfig().utils.pk_field_name, this.objectConfig().utils.label_field_name], // fields
      filters: this.getDataFilters() || [],
      prefilters: this.getDataPreFilters() || [],
      as_geojson: true,
    };
    return this._mData.getList(this.moduleCode(), this.objectCode(), extendedParams);
  }
  refreshData(objectCode: any): void {
    if (objectCode == this.data._object_code) {
      this.postProcessLayout();
    }
  }
}
