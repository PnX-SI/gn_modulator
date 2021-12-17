const defautDrawOptions = {
  position: 'topleft',
}

export default {

  /** Initialise le composant geoman */
  initDraw(mapId, drawOptions) {
    const map = this.getMap(mapId);
    if (!map) return;
    drawOptions = drawOptions || defautDrawOptions;
    map.pm.addControls(drawOptions);
  },

  setDrawOptions(mapId, drawOptions) {
    map.pm.setDrawOptions(drawOptions)
  }
}