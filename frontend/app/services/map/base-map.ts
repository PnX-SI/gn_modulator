import * as L from '@librairies/leaflet';

export default {
  formatBaseMapConfig(baseMap) {
    // tslint:disable-next-line:forin
    for (let attr in baseMap) {
      if (attr === 'layer') {
        baseMap['url'] = baseMap[attr];
        delete baseMap['layer'];
      }
      if (!['url', 'layer', 'name', 'service', 'options'].includes(attr)) {
        if (!baseMap['options']) {
          baseMap['options'] = {};
        }
        baseMap['options'][attr] = baseMap[attr];
        delete baseMap[attr];
      }
    }
    return baseMap;
  },

  addBaseMap(mapId, skip_ref_layers) {
    const map = this.getMap(mapId);
    const baseControl = {};
    const BASEMAP = JSON.parse(JSON.stringify(this._mConfig.appConfig().MAPCONFIG.BASEMAP));

    BASEMAP.forEach((basemap, index) => {
      const formatedBasemap = this.formatBaseMapConfig(basemap);
      if (basemap.service === 'wms') {
        baseControl[formatedBasemap.name] = L.tileLayer.wms(
          formatedBasemap.url,
          formatedBasemap.options,
        );
      } else {
        baseControl[formatedBasemap.name] = L.tileLayer(
          formatedBasemap.url,
          formatedBasemap.options,
        );
      }
      if (index === 0) {
        map.addLayer(baseControl[basemap.name]);
      }
    });

    const overlaysLayers = this.createOverLayers(map, skip_ref_layers);
    map.controls = L.control.layers(baseControl, overlaysLayers);
    map.controls.addTo(map);
  },

  // redéfinition de la fonction de mapservice de gn
  createOverLayers(map, skip_ref_layers) {
    const OVERLAYERS = JSON.parse(JSON.stringify(this._gnMapService.config.MAPCONFIG.REF_LAYERS));
    const overlaysLayers = {};
    OVERLAYERS.map((lyr) => [lyr, this._gnMapService.getLayerCreator(lyr.type)(lyr)])
      .filter((l) => l[1] && !skip_ref_layers.includes(l[0].code))
      .forEach((lyr) => {
        let title = lyr[0]?.label || '';
        let style = lyr[0]?.style || {};

        // this code create dict for L.controler.layers
        // key is name display as checkbox label
        // value is layer
        let layerLeaf = lyr[1];
        let legendUrl = '';
        layerLeaf.configId = lyr[0].code;
        if (layerLeaf?.options?.service === 'wms' && layerLeaf._url) {
          legendUrl = `${layerLeaf._url}?TRANSPARENT=TRUE&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=${layerLeaf.options.layers}&FORMAT=image%2Fpng&LEGEND_OPTIONS=forceLabels%3Aon%3BfontAntiAliasing%3Atrue`;
        }
        // leaflet layers controler required object
        if (this._gnMapService.config.MAPCONFIG?.REF_LAYERS_LEGEND) {
          overlaysLayers[
            this._gnMapService.getLegendBox({ title: title, ...style, legendUrl: legendUrl })
          ] = lyr[1];
        } else {
          overlaysLayers[`<span data-qa="title-overlay">${title}</span>`] = lyr[1];
        }
        if (lyr[0].activate) {
          map.addLayer(layerLeaf);
          this._gnMapService.loadOverlay(layerLeaf);
        }
      });
    return overlaysLayers;
  },
};
