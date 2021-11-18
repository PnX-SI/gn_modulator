/**
 * Methodes pour gérer les layers
 * destinées à ModulesMapService
 */

import utils from '../../utils';

const defaultLayerOptions = {
  bZoom: false,
  bCluster: false,
  onEachFeature: () => {console.log('uu')},
  style: null
}

export default {

  processLayersData(mapId, layersData) {
    /**
     * layersData: {
     *  ...
     *  <key>: {
     *    label,
     *    geojson,
     *    options: {
     *        bZoom,
     *        bCluster,
     *        onEachFeature,
     *        style
     *    }
     *  },
     *  ...
     * }
     */

    if(!this.getMap(mapId)) {
      return;
    }

    if (!layersData) {
      return;
    }

    this._layersData[mapId] = this._layersData[mapId] || {};


    for (const [key, value] of Object.entries(layersData)) {
      this.removeLayers(mapId, { key } );
      this.loadGeojson(mapId, key, value['geojson'], value['layerOptions'])
      this._layersData[mapId][key] = value;
    }
  },

  layers(mapId) {
    const map = this.getMap(mapId);
    if(!map) return;
    return Object.values(map._layers);
  },

  findLayer(mapId, key, id) {
    const map = this.getMap(mapId);
    if(!map) return;
    return this.layers(mapId)
      .find((layer) => layer.key == key && layer.id == id);
  },

  removeLayers(mapId, filters = {}) {
    const map = this.getMap(mapId);
    if (!map) return;

    for (const layer of this.filterLayers(mapId, filters)) {
      map.removeLayer(layer);
    };
  },

  filterLayers(mapId, filters = {}) {
    const map = this.getMap(mapId);
    if (!map) return;
    var layers = this.layers(mapId)
    return this.layers(mapId).filter((layer) => {
      return Object.entries(filters).every(([key, value]) => {
        const layerValue = layer[key]
          || layer.feature && layer.feature.properties && layer.feature.properties[key];
        return Array.isArray(value)
          ? value.includes(layerValue)
          : value == layerValue
      });
    });
  },

  loadGeojson(mapId, key, geojson, layerOptions) {

    const map = this.getMap(mapId);

    layerOptions = layerOptions || defaultLayerOptions
    layerOptions.key = key;

    const currentGeojson = this.createlayersFromGeojson(
      geojson,
      layerOptions
    );

    const layerGroup = new this.L.FeatureGroup();
    layerGroup.key = key;
    map.addLayer(layerGroup);
    layerGroup.addLayer(currentGeojson);
    if (layerOptions.bZoom) {
      this.zoomOnLayer(mapId, layerGroup);
    }
  },

  zoomOnLayer(mapId, layer) {
    if (!layer) {
      return;
    }
    const map=this.getMap(mapId, layer.getBounds);

    setTimeout(() => {
      if (!layer.getBounds) {
        // zoom on point ???
        return;
      }

      let bounds = layer.getBounds();
      if (!Object.keys(bounds).length) {
        return;
      }

      map.fitBounds(layer.getBounds());
    }, 200);

  },

  createlayersFromGeojson(
    geojson,
    {
      asCluster=null,
      onEachFeature=null,
      style=null,
      type=null,
      key=null,
    } = {}
  ) : any {
    const geojsonLayer = this.L.geoJSON(
      geojson,
      {
        style: feature => {
          switch (feature.geometry.type) {
            // No color nor opacity for linestrings
            case 'LineString':
              return style
                ? style
                : {
                    color: '#3388ff',
                    weight: 3
                };
            default:
              return style
                ? style
                : {
                    color: '#3388ff',
                    fill: true,
                    fillOpacity: 0.2,
                    weight: 3
                };
          }
        },
        pointToLayer: (feature, latlng) => {
          if(type == 'marker') {
            return this.L.marker(latlng);
          }
          return this.L.circleMarker(latlng);
        },
        onEachFeature: (feature, layer) => {
          layer.key = key;
          if (!!onEachFeature) {
            return onEachFeature(feature, layer)
          }
        }
      }
    );
    if (asCluster) {
      return (this.L as any)
        .markerClusterGroup()
        .addLayer(geojsonLayer);
    }
    return geojsonLayer;
  },

  actionTooltipDisplayZoomThreshold(
    mapId,
    layer,
    tooltipDisplayZoomTreshold,
    tooltipDisplayed,
    zoomLevel,
    mapBounds,
    lastZoomLevel=null,
    lastMapBounds=null
  ) {

    zoomLevel = zoomLevel || this.getZoom(mapId);
    mapBounds = mapBounds || this.getMapBounds(mapId);

    // TODO gerer les autres geoms ??
    if(!(layer.getLatLng)) {
      return
    }

    const condZoomChanged = (
      !lastZoomLevel
      || ( zoomLevel < tooltipDisplayZoomTreshold && lastZoomLevel >= tooltipDisplayZoomTreshold )
      || ( zoomLevel >= tooltipDisplayZoomTreshold && lastZoomLevel <= tooltipDisplayZoomTreshold )
    )

    const condMapBoundsChanged = !mapBounds || !utils.fastDeepEqual(mapBounds, lastMapBounds);

    if (!(condZoomChanged || condMapBoundsChanged)) {
      return;
    }

    const condInBounds = mapBounds.contains(layer.getLatLng());
    const condZoom = zoomLevel >= tooltipDisplayZoomTreshold;
    /** Les cas ou l'on doit effacer le tooltip */
    if (
      (tooltipDisplayed && !( condInBounds && condZoom ) )
    ) {
      return 'hide';
    }

    else if (
      !tooltipDisplayed && (condZoom && condInBounds)
    ) {
      return 'display';
    }
  },

  layerZoomMoveEndListener(mapId, layer, tooltipDisplayZoomTreshold) {
    // on garde en mémoire le dernier zoom
    var lastZoomLevel;
    var lastMapBounds;

    return (zoomLevel, mapBounds) => {

      const tooltip = layer.getTooltip();
      if (!tooltip) {
        return;
      }
      const tooltipDisplayed = tooltip.options.permanent;
      const action = this.actionTooltipDisplayZoomThreshold(
        mapId,
        layer,
        tooltipDisplayZoomTreshold,
        tooltipDisplayed,
        zoomLevel ,
        mapBounds,
        lastZoomLevel,
        lastMapBounds);

      if( action == 'display') {
        const tooltip = layer.getTooltip();
        layer.unbindTooltip().bindTooltip(tooltip, {permanent: true})
      }

      if (action == 'hide') {
        const tooltip = layer.getTooltip();
        layer.unbindTooltip().bindTooltip(tooltip, {permanent: false})
      }

      lastZoomLevel = zoomLevel;
      lastMapBounds = mapBounds;
    }
  }
}

