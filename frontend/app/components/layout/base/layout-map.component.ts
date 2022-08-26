import { Component, OnInit, Injector } from "@angular/core";
import { ModulesLayoutService } from "../../../services/layout.service";
import { ModulesMapService } from "../../../services/map.service";
import { ModulesLayoutComponent } from "./layout.component";
import { MediaService } from "@geonature_common/service/media.service";
import utils from "../../../utils";
@Component({
  selector: "modules-layout-map",
  templateUrl: "layout-map.component.html",
  styleUrls: ["../../base/base.scss", "layout-map.component.scss"],
})
export class ModulesLayoutMapComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  _mapService: ModulesMapService;

  mapId; // identifiant HTML pour la table;
  _map;

  editedLayerSubscription;
  modalData = {};
  modalsLayout: any;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-map";
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
    if (["cancel", "submit-gps"].includes(event.action)) {
      this._mLayout.closeModals();
    }

    /** validation gps */
    if (event.action == "submit-gps") {
      this._map.$editedLayer.next({
        type: "Point",
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
      this.editedLayerSubscription = this._map.$editedLayer.subscribe(
        (layer) => {
          layer && this.onEditedLayerChange(layer);
        }
      );
    }
  }

  /**
   * Ici on va gérer les données pour l'affichage sur la carte
   *  data -> layoutData
   */
  postComputeLayout(dataChanged, layoutChanged): void {
    if (this.computedLayout.map_id) {
      this.mapId = this.computedLayout.map_id;
    }
    this._mapService.initMap(this.mapId).then((map) => {
      this._map = map;

      if (layoutChanged) {
        this.processDrawConfig();
      }

      // affichage des données

      if (dataChanged) {
        this._mapService.processData(this.mapId, this.data, {
          key: this.computedLayout.key,
        });

        return;
      }

      // initialisation de edited layer si besoin
      if (
        this.computedLayout.key &&
        this.data[this.computedLayout.key] &&
        this.computedLayout.edit &&
        !this._map.$editedLayer.getValue()
      ) {
        // TODO faire un layer
        this._map.$editedLayer.next(this.data[this.computedLayout.key]);
      }
    });
  }

  onEditedLayerChange(layer) {
    if (this.computedLayout.key) {
      const dataGeom = layer.toGeoJSON
        ? layer.toGeoJSON().geometry
        : layer.coordinates
        ? layer
        : null;

      this.data[this.computedLayout.key] = dataGeom;

      this._mLayout.reComputeLayout("map");
    }
  }

  onHeightChange(): void {
    this._mapService.waitForMap(this.mapId).then((map) => {
      map.invalidateSize();
    });
  }
}
