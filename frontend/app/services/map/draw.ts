import { Observable, Subject, BehaviorSubject } from "@librairies/rxjs";
import utils from "../../utils";

const defautDrawOptions = {
  position: "topleft",
  drawMarker: true,
  editMode: true,
  drawCircle: false,
  drawCircleMarker: false,
  drawRectangle: false,
  drawPolygon: false,
  drawText: false,
  drawPolyline: false,
  dragMode: false,
  cutPolygon: false,
  removalMode: false,
  rotateMode: false,
};

const hiddenDrawOptions = {
  drawCircle: false,
  drawCircleMarker: false,
  drawRectangle: false,
  drawMarker: false,
  drawPolygon: false,
  drawPolyline: false,
  drawText: false,
  dragMode: false,
  editMode: false,
  cutPolygon: false,
  removalMode: false,
  rotateMode: false,
};

export default {
  // layer pour l'edition

  /** Initialise le composant geoman */
  // initDraw(mapId, drawOptions) {
  //   const map = this.getMap(mapId);
  //   if (!map) return;
  //   drawOptions = drawOptions || defautDrawOptions;
  //   // map.pm.setDrawOptions(drawOptions);
  //   map.pm.addControls(drawOptions);
  // },


  /**
   *  options: {
   *    edit: si l'edition est permise
   *    drawOptions: {...} option de geoman,
   *    gps: boolean,
   * }
   */
  setDrawConfig(mapId, options) {
    const map = this.getMap(mapId);
    if (!map) return;

    // gestion des options de geoman
    const drawOptions = options.edit
      ? (options.drawOptions || defautDrawOptions)
      : hiddenDrawOptions;

    if(!utils.fastDeepEqual(drawOptions, map.drawOptions)) {
      map.drawOptions = drawOptions;
      map.pm.addControls(drawOptions);
    }


    // init $editedLayer
    if (!map.$editedLayer) {
      this.initEditedLayer(mapId);
    }

    // gps
    if (options.gps && !map.gps) {
      map.gps = true;
      this.addMapControl(mapId, 'gps')
    }

  },

  /** pour faire le liens entre les évènement de geoman (pm:create, pm:edit)
   * et l'observable map.$editedLayer
  */
  initEditedLayer(mapId) {
    const map = this.getMap(mapId);
    if (!map) return;

    map.$editedLayer = new BehaviorSubject(null);
    map.on("pm:create", (event) => {
      // remove previous layer if needed
      if (map.$editedLayer.getValue()) {
        // on efface le layer avant d'en afficher un nouveau
        map.removeLayer(map.$editedLayer.getValue());
      }
      map.$editedLayer.next(event.layer);
      // on edit
      event.layer.on("pm:edit", ({ layer }) => {
        map.$editedLayer.next(layer);
      });
    });
  },

};
