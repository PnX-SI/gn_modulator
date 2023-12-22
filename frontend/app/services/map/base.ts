import utils from '../../utils';
import * as L from '@librairies/leaflet';

export default {
  waitForMap(mapId, maxRetries = null): Promise<L.map> {
    let index = 1;
    return new Promise((resolve, reject) => {
      const intervalId = setInterval(() => {
        const map = this.getMap(mapId);
        if (map && map.isInitialized) {
          clearInterval(intervalId);
          resolve(map);
          return;
        }
        index += 1;
        if (maxRetries && index > maxRetries) {
          clearInterval(intervalId);
          console.error(
            `La carte attendue ${mapId} n'est pas présente (index > maxRetries=${maxRetries})`,
          );
          reject();
          return;
        }
      }, 250);
    });
  },

  setMap(mapId, map) {
    this._maps[mapId] = map;
  },

  getMap(mapId): L.map {
    return this._maps[mapId];
  },

  computeCenter(center: any = null) {
    let computedCenter;
    if (!!center) {
      computedCenter =
        Array.isArray(center) && center.length == 2
          ? this.L.latLng(center[0], center[1])
          : this.computeGeometryCenter(center);
    }

    // centre dpuis le
    if (this._mapSettingsSave.center) {
      return this._mapSettingsSave.center;
    }

    computedCenter =
      computedCenter ||
      this.L.latLng(
        this._mConfig.appConfig().MAPCONFIG.CENTER[0],
        this._mConfig.appConfig().MAPCONFIG.CENTER[1],
      );
    return computedCenter;
  },

  computeGeometryCenter(geom) {
    if (['Polygon', 'LineString'].includes(geom.type)) {
      const centroid = this.getCentroid(geom.coordinates[0]);
      return L.latLng(centroid[1], centroid[0]);
    }
    if (['Point'].includes(geom.type)) {
      return L.latLng(geom.coordinates[1], geom.coordinates[0]);
    }
  },

  getCentroid(arr) {
    return arr.reduce(
      (x, y) => {
        return [x[0] + y[0] / arr.length, x[1] + y[1] / arr.length];
      },
      [0, 0],
    );
  },

  computeZoom(zoom = null) {
    return zoom || this._mapSettingsSave.zoom || this._mConfig.appConfig().MAPCONFIG.ZOOM_LEVEL;
  },

  setCenter(mapId, center: any = null) {
    if (!this.getMap(mapId)) {
      return;
    }
    this.getMap(mapId).panTo();
  },

  setZoom(mapId, zoom = null) {
    if (!this.getMap(mapId)) {
      return;
    }
    this.getMap(mapId).setZoom(this.computeZoom());
  },

  setView(mapId, center = null, zoom = null) {
    if (!this.getMap(mapId)) {
      return;
    }
    this.getMap(mapId).flyTo(center, zoom);
  },

  getZoom(mapId) {
    if (!this.getMap(mapId)) {
      return;
    }
    return this.getMap(mapId) && this.getMap(mapId).getZoom();
  },

  getCenter(mapId, asArray = false) {
    if (!this.getMap(mapId)) {
      return;
    }
    const center = this.getMap(mapId) && this.getMap(mapId).getCenter();
    if (!asArray) {
      return center;
    }
    return [center.lat, center.lng];
  },

  getMapBounds(mapId) {
    if (!this.getMap(mapId)) {
      return;
    }
    return this.getMap(mapId) && this.getMap(mapId).getBounds();
  },

  getMapBoundsArray(mapId) {
    const bounds = this.getMapBounds(mapId);
    return (
      bounds && [
        bounds._southWest.lng,
        bounds._southWest.lat,
        bounds._northEast.lng,
        bounds._northEast.lat,
      ]
    );
  },

  getMapBoundsFilterValue(mapId) {
    const boundsArray = this.getMapBoundsArray(mapId);
    return boundsArray && boundsArray.join(';');
  },

  initMap(
    mapId,
    { zoom = null, center = null, bEdit = null, drawOptions = null, skip_ref_layers = [] } = {},
  ) {
    if (this._pendingMaps[mapId]) {
      return this.waitForMap(mapId);
    }
    this._pendingMaps[mapId] = true;

    return new Promise((resolve) => {
      utils.waitForElement(mapId).then(() => {
        const map = this.L.map(document.getElementById(mapId), {
          zoomControl: false,
          preferCanvas: true,
          center: this.computeCenter(center),
          zoom: this.computeZoom(zoom),
          zoomSnap: 0.1,
        });
        this.setMap(mapId, map);

        setTimeout(() => {
          /** zoom scale */
          this.L.control.zoom({ position: 'topright' }).addTo(map);
          this.L.control.scale().addTo(map);

          /** set baseMaps (from geonature config) */

          this.addBaseMap(mapId, skip_ref_layers);

          /** listen to moveend and zoomend */

          const fnMapZoomMoveEnd = () => {
            const zoomLevel = this.getZoom(mapId);
            const mapBounds = this.getMapBounds(mapId);
            const center = this.getCenter(mapId);
            this._mapSettingsSave.zoom = zoomLevel;
            this._mapSettingsSave.center = center;

            this._mLayout.reComputeLayout('map zoom end');
            map.eachLayer((l) => {
              l.onZoomMoveEnd && l.onZoomMoveEnd(zoomLevel, mapBounds);
            });
          };

          map.on('moveend', fnMapZoomMoveEnd);
          map.on('zoomend', fnMapZoomMoveEnd);

          /** coords on rigth click */
          map.on('contextmenu', (event: any) => {
            map.coordinatesTxt = `${event.latlng.lng}, ${event.latlng.lat}`;
            navigator.clipboard.writeText(`${event.latlng.lng}, ${event.latlng.lat}`);
          });

          map.isInitialized = true;

          resolve(map);
        }, 100);
      });
    });
  },
};
