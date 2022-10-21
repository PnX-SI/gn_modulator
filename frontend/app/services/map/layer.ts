/**
 * Methodes pour gérer les layers
 * destinées à ModulesMapService
 */

import utils from '../../utils';

const defaultLayerOptions = {
  bZoom: false,
  bCluster: false,
  onEachFeature: () => {},
  style: null,
};

export default {
  /**
   * retourne le type de données
   * - geometry
   * - feature
   * - features-collection ou array ?
   * - plusieurs features collection (trouvder un nom)
   */
  getDataType(data) {
    if (data.coordinates && data.type) {
      return 'geometry';
    }

    if (data.type == 'Feature') {
      return 'feature';
    }

    if (utils.isObject(data) && Object.keys(data).length) {
      return 'dict';
    }
  },

  /**
   * plusieurs cas
   *  - data geom
   */
  processData(mapId, data, options: any = {}) {
    if (!data) {
      return;
    }
    const dataType = this.getDataType(data);

    if (!dataType) {
      return;
    }

    if (options.key && data[options.key]) {
      this.removeLayers(mapId, { key: options.key });
      return this.processData(mapId, data[options.key], options);
    }
    if (dataType == 'geometry') {
      return this.processGeometry(mapId, data, options);
    }
    if (dataType == 'dict') {
      return this.processLayersData(mapId, data);
    }
  },

  processGeometry(mapId, data, options) {
    const layer = this.L.geoJSON(data, {
      pointToLayer: (feature, latlng) => {
        return this.L.circleMarker(latlng);
      },
    });
    layer.key = options.key;
    this.getMap(mapId)._layers;
    this.getMap(mapId).addLayer(layer);

    if (options.zoom) {
      this.zoomOnLayer(mapId, layer);
    }
    return layer;
  },

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

    if (!this.getMap(mapId)) {
      return;
    }

    if (!layersData) {
      return;
    }

    this._layersData[mapId] = this._layersData[mapId] || {};

    for (const [key, value] of Object.entries(layersData)) {
      if (!value) {
        continue;
      }
      this.removeLayers(mapId, { key });
      this.loadGeojson(mapId, key, value['geojson'], value['layerOptions']);
      this._layersData[mapId][key] = value;
    }
  },

  layers(mapId) {
    const map = this.getMap(mapId);
    if (!map) return;
    return Object.values(map._layers);
  },

  findLayer(mapId, filters) {
    const map = this.getMap(mapId);
    if (!map) return;
    const layers = this.filterLayers(mapId, filters);
    return layers.length == 1 ? layers[0] : null;
  },

  removeLayers(mapId, filters = {}) {
    const map = this.getMap(mapId);
    if (!map) return;

    for (const layer of this.filterLayers(mapId, filters)) {
      map.removeLayer(layer);
    }
  },

  layerValue(layer, key) {
    return (
      layer[key] || (layer.feature && layer.feature.properties && layer.feature.properties[key])
    );
  },

  filterLayers(mapId, filters = {}) {
    const map = this.getMap(mapId);
    if (!map) return;
    var layers = this.layers(mapId);
    return this.layers(mapId).filter((layer) => {
      return Object.entries(filters).every(([key, value]) => {
        const layerValue = this.layerValue(layer, key);
        return Array.isArray(value) ? value.includes(layerValue) : value == layerValue;
      });
    });
  },

  loadGeojson(mapId, key, geojson, layerOptions) {
    const map = this.getMap(mapId);

    layerOptions = layerOptions || defaultLayerOptions;
    layerOptions.key = key;

    const currentGeojson = this.createlayersFromGeojson(geojson, layerOptions);

    const layerGroup = new this.L.FeatureGroup();
    layerGroup.key = key;
    map.addLayer(layerGroup);
    layerGroup.addLayer(currentGeojson);

    // onLayersAdded : action effectuée après l'ajout des layers
    if (layerOptions.onLayersAdded) {
      setTimeout(() => {
        layerOptions.onLayersAdded();
      }, 1000);
    }
    if (layerOptions.zoom) {
      this.zoomOnLayer(mapId, layerGroup);
    }
  },

  zoomOnLayer(mapId, layer) {
    if (!layer) {
      return;
    }
    const map = this.getMap(mapId);
    if (layer.getLatLng) {
      this.setCenter(mapId, utils.copy(layer.getLatLng()));
      return
    }

    setTimeout(() => {
      if (!layer.getBounds) {
        // zoom on point ???
        return;
      }

      let bounds = layer.getBounds();
      if (!Object.keys(bounds).length) {
        return;
      }

      if (utils.fastDeepEqual(bounds._northEast, bounds._southWest)) {
        this.setCenter(mapId, [ bounds._northEast.lat,  bounds._northEast.lng ] );
        return;
      }

      map.fitBounds(layer.getBounds());
    }, 100);
  },

  createlayersFromGeojson(
    geojson,
    {
      asCluster = null,
      onEachFeature = null,
      style = null,
      type = null,
      key = null,
      pane = null,
      bring_to_front = null,
    } = {}
  ): any {
    const geojsonLayer = this.L.geoJSON(geojson, {
      pane,
      style: (feature) => {
        switch (feature.geometry.type) {
          // No color nor opacity for linestrings
          case 'LineString':
            return style
              ? style
              : {
                  color: '#3388ff',
                  weight: 3,
                };
          default:
            return style
              ? style
              : {
                  color: '#3388ff',
                  fill: true,
                  fillOpacity: 0.2,
                  weight: 3,
                };
        }
      },
      pointToLayer: (feature, latlng) => {
        if (type == 'marker') {
          return this.L.marker(latlng, { pane });
        }
        return this.L.circleMarker(latlng, { pane });
      },
      onEachFeature: (feature, layer) => {
        layer.key = key;
        if (bring_to_front) {
          setTimeout(() => {
            layer.bringToFront();
          }, 500);
        }
        if (!!onEachFeature) {
          return onEachFeature(feature, layer);
        }
      },
    });
    if (asCluster) {
      return (this.L as any).markerClusterGroup().addLayer(geojsonLayer);
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
    lastZoomLevel = null,
    lastMapBounds = null
  ) {
    zoomLevel = zoomLevel || this.getZoom(mapId);
    mapBounds = mapBounds || this.getMapBounds(mapId);

    // TODO gerer les autres geoms ??
    if (!layer.getLatLng) {
      return;
    }

    const condZoomChanged =
      !lastZoomLevel ||
      (zoomLevel < tooltipDisplayZoomTreshold && lastZoomLevel >= tooltipDisplayZoomTreshold) ||
      (zoomLevel >= tooltipDisplayZoomTreshold && lastZoomLevel <= tooltipDisplayZoomTreshold);

    const condMapBoundsChanged = !mapBounds || !utils.fastDeepEqual(mapBounds, lastMapBounds);

    if (!(condZoomChanged || condMapBoundsChanged)) {
      return;
    }

    const condInBounds = mapBounds.contains(layer.getLatLng());
    const condZoom = zoomLevel >= tooltipDisplayZoomTreshold;
    /** Les cas ou l'on doit effacer le tooltip */
    if (tooltipDisplayed && !(condInBounds && condZoom)) {
      return 'hide';
    } else if (!tooltipDisplayed && condZoom && condInBounds) {
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
        zoomLevel,
        mapBounds,
        lastZoomLevel,
        lastMapBounds
      );

      if (action == 'display') {
        const tooltip = layer.getTooltip();
        layer.unbindTooltip().bindTooltip(tooltip, { permanent: true });
      }

      if (action == 'hide') {
        const tooltip = layer.getTooltip();
        layer.unbindTooltip().bindTooltip(tooltip, { permanent: false });
      }

      lastZoomLevel = zoomLevel;
      lastMapBounds = mapBounds;
    };
  },

  setProcessing(mapId, bIsProcessing) {
    this.waitForMap(mapId).then((map) => {
      map.isProcessing = bIsProcessing;
    });
  },
};
