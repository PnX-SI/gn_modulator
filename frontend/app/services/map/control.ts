/**
 * Les controls pour la carte
 */
import controlConfigs from './control-layouts';

export default {
  _controls: {}, // pour pouvoir acceder aux controls

  _controlConfigs: controlConfigs,

  /**
   * ajoute un control sur la carte
   * - gps
   */
  addControl(mapId, { controlId, label, onClick, position = 'topleft', controlLogoUrl }) {
    const map = this.getMap(mapId);
    if (!map) {
      return;
    }

    // si le controle existe, on ne le rajoute pas une deuxième fois
    if (map._controls && map._controls[controlId]) {
      return;
    }

    const CustomControl = this.L.Control.extend({
      options: {
        position,
      },
      onAdd: (map) => {
        const customControl = this.L.DomUtil.create(
          'div',
          'leaflet-bar leaflet-control leaflet-control-custom',
        );
        customControl.id = controlId;
        customControl.style.width = '34px';
        customControl.style.height = '34px';
        customControl.style.lineHeight = '30px';
        customControl.style.backgroundColor = 'white';
        customControl.style.cursor = 'pointer';
        customControl.style.border = '2px solid rgba(0,0,0,0.2)';
        customControl.style.backgroundImage = controlLogoUrl;
        customControl.style.backgroundRepeat = 'no-repeat';
        customControl.style.backgroundPosition = '7px';
        customControl.style.textAlign = 'center';
        customControl.innerHTML = label ? `<b>${label}</b>` : null;
        customControl.onclick = () => {
          if (onClick) {
            onClick();
          }
        };
        return customControl;
      },
    });

    const customControl = new CustomControl();
    map.addControl(customControl);

    // sauvegarde du control
    map._controls = map._controls || {};
    map._controls[controlId] = customControl;
  },

  /** ajout d'un layout en lien avec un control
   * par exemple le formulaire lat-lon pour le gps
   */
  addMapLayout(mapId, layoutToAdd) {
    const map = this.getMap(mapId);
    if (!(map && layoutToAdd)) {
      return;
    }

    map.layout = map.layout || [];
    map.layout.push(layoutToAdd);
  },

  addMapControl(mapId, controlId) {
    const map = this.getMap(mapId);
    if (!map) return;

    // si le controle existe deja on retourne
    if (map._controls && map._controls[controlId]) return;

    const controlConfig = this._controlConfigs[controlId];
    if (!controlConfig) {
      return;
    }

    // ajout du controle
    this.addControl(mapId, {
      label: controlConfig.label,
      controlId,
      onClick: controlConfig.onControlClick.bind(this)(mapId),
    });

    // ajout du layout
    this.addMapLayout(mapId, controlConfig.layout);
  },
};
