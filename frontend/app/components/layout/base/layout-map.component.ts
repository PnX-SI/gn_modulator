import { Component, OnInit, Injector } from '@angular/core';
import { ModulesMapService } from '../../../services/map.service';
import { ModulesLayoutComponent } from './layout.component';
import utils from '../../../utils';
@Component({
  selector: 'modules-layout-map',
  templateUrl: 'layout-map.component.html',
  styleUrls: ['../../base/base.scss', 'layout-map.component.scss'],
})
export class ModulesLayoutMapComponent extends ModulesLayoutComponent implements OnInit {
  _mapService: ModulesMapService;

  mapId; // identifiant HTML pour la table;
  _map;

  firstEdit = true;

  editedLayerSubscription;
  modalData = {};
  modalsLayout: any;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = 'layout-map';
    this._mapService = this._injector.get(ModulesMapService);
    this.mapId = `map_${this._id}`;
    this.bPostComputeLayout = true;
  }

  /** initialisaiton de la carte */
  postInit(): void {}

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
    if (!this.editedLayerSubscription) {
      this.editedLayerSubscription = this._map.$editedLayer.subscribe((layer) => {
        layer && this.onEditedLayerChange(layer);
      });
    }
  }

  postProcessContext(): void {
    this.context.map_id = this.mapId;
  }

  /**
   * Ici on va gérer les données pour l'affichage sur la carte
   *  data -> layoutData
   */
  postComputeLayout(dataChanged, layoutChanged): void {
    this._mapService.initMap(this.mapId, { zoom: this.computedLayout.zoom }).then((map) => {
      this._map = map;

      if (layoutChanged) {
        this.processDrawConfig();
      }

      // affichage des données

      if (dataChanged && this.computedLayout.key) {
        const layer = this._mapService.processData(this.mapId, this.data, {
          key: this.computedLayout.key,
          zoom: this.computedLayout.zoom && this.firstEdit,
        });

        // initialisation du layer d'edition (s'il edit est à true et s'il n'est pas déjà )
        if (this.computedLayout.edit && !this._map.$editedLayer.getValue()) {
          this._map.$editedLayer.next(layer);
          this.firstEdit = false;
          // this._mapService.zoomOnLayer(this.mapId, layer);
        }
      }
    });
  }

  onEditedLayerChange(layer) {
    if (this.computedLayout.key) {
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

      this.data[this.computedLayout.key] = dataGeom;
      this._mLayout.reComputeLayout('map');
    }
  }

  onHeightChange(): void {
    this._mapService.waitForMap(this.mapId).then((map) => {
      map.invalidateSize();
    });
  }

  refreshData(objectCode: any): void {}
}
