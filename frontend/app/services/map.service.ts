import { Injectable } from "@angular/core";

import { ModulesConfigService } from "./config.service";
import * as L from '@librairies/leaflet';
import '@librairies/@geoman-io/leaflet-geoman-free';
// import {CustomIcon} from '@geonature/utils/leaflet-icon';


// delete L.Icon.Default.prototype['_getIconUrl'];
// L.Icon.Default.mergeOptions(CustomIcon);

// delete L.Icon.Default.prototype['_getIconUrl'];

// const iconRetinaUrl = 'assets/marker-icon-2x.png';
// const iconUrl = 'assets/marker-icon.png';
// const shadowUrl = 'assets/marker-shadow.png';
// const iconDefault = L.icon({
//   iconRetinaUrl,
//   iconUrl,
//   shadowUrl,
//   iconSize: [25, 41],
//   iconAnchor: [12, 41],
//   popupAnchor: [1, -34],
//   tooltipAnchor: [16, -28],
//   shadowSize: [41, 41]
// });

// delete L.Icon.Default.prototype['_getIconUrl'];
// L.Icon.Default.mergeOptions(iconDefault);
// L.Marker.prototype.options.icon = iconDefault;

L.PM.initialize({ optIn: true }); // Property 'PM' does not exist on type 'typeof import(".../node_modules/@types/leaflet/index")'.ts(2339)


import mapMethods from './map'

@Injectable()
export class ModulesMapService {

  constructor(
    private _config: ModulesConfigService,
  ) {
    /** on récupère touts les méthodes definies dans les fichiers du répertoire ./map/ */
    for (const methods of Object.values(mapMethods)) {
      for (const [key, value] of Object.entries(methods)) {
        this[key]=value
      }
    }
  }


  /** map cache: {..., <mapId>: map,...} */
  _maps = {};

  /** layerDataCache */
  _layersData = {};

  /** Leaflet */
  L=L;

  /** Configuration */

  init() {
  }


  /** Methodes pour la carte*/


  /**
   * methodes depuis les fichiers de ./map/
   */


  /** ./map/base */

  initMap = mapMethods.base.initMap;
  waitForMap = mapMethods.base.waitForMap;

  getMap = mapMethods.base.getMap;
  getZoom = mapMethods.base.getZoom;
  getCenter = mapMethods.base.getCenter;
  getMapBounds = mapMethods.base.getMapBounds;

  setView = mapMethods.base.setView;
  setCenter = mapMethods.base.setCenter;
  setZoom = mapMethods.base.setZoom;


  /** ./map/baseMap */

  addBaseMap = mapMethods.base_map.addBaseMap;


  /** ./map/layers */

  processLayersData = mapMethods.layer.processLayersData;
  layerZoomMoveEndListener = mapMethods.layer.layerZoomMoveEndListener;
  actionTooltipDisplayZoomThreshold = mapMethods.layer.actionTooltipDisplayZoomThreshold;
  findLayer = mapMethods.layer.findLayer;

  /** ./map/draw */

  initDraw = mapMethods.draw.initDraw;
  setDrawOptions = mapMethods.draw.setDrawOptions;

}