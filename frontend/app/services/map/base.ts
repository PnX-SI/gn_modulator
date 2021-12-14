import utils from  "../../utils"

export default {

  waitForMap(mapId, maxRetries=null) {
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
          console.error(`La carte attendue ${mapId} n'est pas présente (index > maxRetries=${maxRetries})`)
          reject();
          return;
        }
      }, 250);
    })
  },

  setMap(mapId, map) {
    // if(this._maps[mapId]) {
      // console.error(`ModuleMapServices, setMap : La carte ${mapId} existe déjà`)
      // return;
    // }
    this._maps[mapId] = map;
  },

  getMap(mapId) {
      return this._maps[mapId];
  },

  computeCenter(center=null) {
    return center
    ? this.L.latLng(center[0], center[1])
    : this.L.latLng(
        this._config.appConfig().MAPCONFIG.CENTER[0],
        this._config.appConfig().MAPCONFIG.CENTER[1]
    );
  },

  computeZoom(zoom=null) {
    return zoom || this._config.appConfig().MAPCONFIG.ZOOM_LEVEL;
  },

  setCenter(mapId, center=null) {
    if(!this.getMap(mapId)) { return };
    this.getMap(mapId).panTo(this.computeCenter(center));
  },

  setZoom(mapId, zoom=null) {
    if(!this.getMap(mapId)) { return };
    this.getMap(mapId).setZoom(this.computeZoom());
  },

  setView(mapId, center=null, zoom=null) {
    if(!this.getMap(mapId)) { return };
    this.getMap(mapId).flyTo(center, zoom)
  },

  getZoom(mapId) {
    if(!this.getMap(mapId)) { return };
    return this.getMap(mapId) && this.getMap(mapId).getZoom()
  },

  getCenter(mapId, asArray=false) {
    if(!this.getMap(mapId)) { return };
    const center = this.getMap(mapId) && this.getMap(mapId).getCenter()
    if (! asArray) {
      return center;
    }
    return [center.lat, center.lng];
  },

  getMapBounds(mapId) {
    if(!this.getMap(mapId)) { return };
    return this.getMap(mapId) && this.getMap(mapId).getBounds()
  },


  initMap(
    mapId,
    {
      zoom=null,
      center=null,
      bEdit=null,
      drawOptions=null,
    } = {}
  ) {
    utils.waitForElement(mapId).then(() => {
      const map = this.L.map(
        document.getElementById(mapId),
        {
          zoomControl: false,
          preferCanvas: true,
          center: this.computeCenter(center),
          zoom: this.computeZoom(zoom),
          zoomSnap: 0.1
        }
      );
      this.setMap(mapId, map);

      setTimeout(() => {

        /** zoom scale */

        this.L.control.zoom({position: 'topright'}).addTo(map);
        this.L.control.scale().addTo(map);


        /** set baseMaps (from geonature config) */

        this.addBaseMap(mapId);


        /** listen to moveend and zoomend */

        const fnMapZoomMoveEnd = () => {
          const zoomLevel = this.getZoom(mapId)
          const mapBounds = this.getMapBounds(mapId)
          map.eachLayer((l) => {
            l.onZoomMoveEnd && l.onZoomMoveEnd(zoomLevel, mapBounds);
          })
        }

        map.on('moveend', fnMapZoomMoveEnd);
        map.on('zoomend', fnMapZoomMoveEnd);


        /** edit with geoman */
        if (bEdit) {
          this.initDraw(mapId, drawOptions)
        }
        map.isInitialized = true;
      }, 100);

    });
  },

}