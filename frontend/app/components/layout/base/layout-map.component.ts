import { Component, OnInit, Injector, ViewEncapsulation } from '@angular/core';
import { ModulesMapService } from '../../../services/map.service';
import { ModulesLayoutComponent } from './layout.component';
import { Subject } from '@librairies/rxjs';
import { debounceTime } from '@librairies/rxjs/operators';
import utils from '../../../utils';
@Component({
  selector: 'modules-layout-map',
  templateUrl: 'layout-map.component.html',
  styleUrls: ['layout-map.component.scss', '../../base/base.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ModulesLayoutMapComponent extends ModulesLayoutComponent implements OnInit {
  _mapService: ModulesMapService;

  mapId; // identifiant HTML pour la table;
  _map;

  modalData = {};
  modalsLayout: any;

  currentLayer;

  $onMapChanged = new Subject();

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-map';
    this._mapService = this._injector.get(ModulesMapService);
    this.mapId = `map_${this._id}`;
    this.bPostComputeLayout = true;
    this.bCheckParentsHeight = true;
  }

  /** */
  postInit() {
    this._mapService.waitForMap(this.mapId).then((map) => {
      map.on('moveend', () => this.$onMapChanged.next());
      map.on('zoomend', () => this.$onMapChanged.next());
      this._subs['onMapChangedZoomContext'] = this.$onMapChanged
        .pipe(debounceTime(1000))
        .subscribe(() => {
          this.context.map_params = this.context.map_params || {};
          this.context.map_params.bounds_filter_value = this._mapService.getMapBoundsFilterValue(
            this.context.map_id,
          );
          this.context.map_params.zoom = this._mapService.getZoom(this.context.map_id);
          this._mLayout.reComputeLayout('onMapChanged');
        });
      [100, 200, 500, 1000].forEach((t) => setTimeout(() => map.invalidateSize(), t));
    });
  }

  /**
   * action quand un modal (gps, gpx etc... est validé)
   */
  onModalAction(event) {
    /** fermture du modal dans tous les cas */
    if (['cancel', 'submit-gps'].includes(event.action)) {
      this._mLayout.closeModals();
    }

    /** validation gps */
    if (event.action == 'submit-gps') {
      this._map.$editedLayer.next({
        type: 'Point',
        coordinates: [event.data.lon, event.data.lat],
      });
      this._mapService.setCenter(this.mapId, [event.data.lat, event.data.lon]);
    }
  }

  /**
   * afficher cacher les composants geoman
   * souscrire
   * */
  processDrawConfig() {
    // aficher les composants de dessin
    this._mapService.setDrawConfig(this.mapId, this.computedLayout);

    // set de layout
    if (!utils.fastDeepEqual(this.modalsLayout, this._map.layout)) {
      this.modalsLayout = this._map.layout;
    }

    // souscrire aux changements de geometrie
    // (si ce n'est pas déjà fait)
    if (!this._subs['edited_layer']) {
      this._subs['edited_layer'] = this._map.$editedLayer.subscribe((layer) => {
        layer && this.onEditedLayerChange(layer);
      });
    }
  }

  preProcessContext(): void {
    this.context.map_id = this.mapId;
  }

  /**
   * Ici on va gérer les données pour l'affichage sur la carte
   *  data -> layoutData
   */
  postComputeLayout(dataChanged, layoutChanged): void {
    this._mapService.initMap(this.mapId, { ...this.computedLayout }).then((map) => {
      this._map = map;

      if (!this.computedLayout.key) {
        return;
      }

      if (layoutChanged) {
        this.processDrawConfig();
      }
      const geomChanged = !utils.fastDeepEqual(
        this.data[this.computedLayout.key],
        this.dataSave[this.computedLayout.key],
      );

      if (this.currentLayer && geomChanged) {
        console.log('new data!!', this.currentLayer, this.data[this.computedLayout.key]);
      }

      // initialisation
      if (!this.currentLayer && this.data[this.computedLayout.key]) {
        this.currentLayer = this._mapService.processData(this.mapId, this.data, {
          key: this.computedLayout.key,
          zoom: this.computedLayout.zoom,
          title: this.computedLayout.title,
        });
        if (this.computedLayout.edit) {
          this._mapService.layerListenToChange(this.mapId, this.currentLayer);
          this._map.$editedLayer.next(this.currentLayer);
        }
      }
    });
  }

  onEditedLayerChange(layer) {
    if (!this.computedLayout.key) {
      return;
    }
    let dataGeom = null;
    if (layer.toGeoJSON) {
      const layerGeoJson = layer.toGeoJSON();
      dataGeom =
        layerGeoJson.type == 'FeatureCollection'
          ? layerGeoJson.features[0].geometry
          : layerGeoJson.geometry;
    }
    if (layer.coordinates) {
      dataGeom = layer;
    }

    if (utils.fastDeepEqual(this.data[this.computedLayout.key], dataGeom)) {
      return;
    }

    this.data[this.computedLayout.key] = dataGeom;
    this._mLayout.reComputeLayout('map');
  }

  customParentsHeightChange(): void {
    this._mapService.waitForMap(this.mapId).then((map) => {
      map.invalidateSize();
    });
  }

  refreshData(objectCode: any): void {}

  onDestroy() {
    this._mapService.cleanLayers(this.mapId);
  }
}
