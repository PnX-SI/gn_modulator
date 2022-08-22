/**
 * layout pour le gps
 */

export default {
  /** se qui se passe au click du control */
  label: "GPS",
  onControlClick(mapId) {
    return () => {
      const map = this.getMap(mapId);
      if (!map) return;

      const data = {
        lat: null,
        lon: null,
      };
      // si on a un point d'édition =>
      const editedLayer = map.$editedLayer.getValue();

      const dataGeom = editedLayer
        ? editedLayer.toGeoJSON
          ? editedLayer.toGeoJSON().geometry
          : editedLayer
        : null;

      if (dataGeom && dataGeom.type == "Point") {
        data.lat = dataGeom.coordinates[1];
        data.lon = dataGeom.coordinates[0];
      }

      this._mLayout.openModal("gps", data);
    };
  },
  layout: {
    type: "modal",
    modal_name: "gps",
    items: [
      {
        title: "Entrer les coordonnées GPS",
        type: "form",
        items: [
          {
            direction: "row",
            items: [
              {
                type: "number",
                key: "lon",
                title: "Longitude",
                required: true,
              },
              {
                type: "number",
                key: "lat",
                title: "Lattitude",
                required: true,
              },
            ],
          },
          {
            direction: "row",
            items: [
              {
                flex: "initial",
                type: "button",
                color: "primary",
                title: "Valider",
                description: "Valider",
                action: "submit-gps",
                disabled: "__f__!(formGroup.valid )",
              },
              {
                flex: "initial",
                type: "button",
                color: "primary",
                title: "Annuler",
                description: "Annuler",
                action: "cancel",
              },
            ],
          },
        ],
      },
    ],
  },
};
