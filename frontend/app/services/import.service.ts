import { Injectable, Injector } from '@angular/core';
import { ModulesConfigService } from './config.service';
import { ModulesRequestService } from './request.service';
import utils from '../utils';
@Injectable()
export class ModulesImportService {
  _mConfig: ModulesConfigService;
  _mRequest: ModulesRequestService;

  constructor(private _injector: Injector) {
    this._mRequest = this._injector.get(ModulesRequestService);
    this._mConfig = this._injector.get(ModulesConfigService);
  }

  featureRequest(data) {
    return this._mRequest.request('post', `${this._mConfig.backendModuleUrl()}/import_feature`, {
      data,
    });
  }

  importRequest(moduleCode, object_code, data, params = {}, admin = false) {
    const urlPartAdmin = admin ? '_admin' : '';
    return this._mRequest.postRequestWithFormData(
      `${this._mConfig.backendModuleUrl()}/import_async${urlPartAdmin}/${moduleCode}/${object_code}/${
        data.id_import || ''
      }`,
      {
        data: data.id_import ? {} : data,
        params,
      },
    );
  }

  processMessage(data) {
    if (!data.id_import) {
      return {
        html: `
          <b>Veuillez choisir un fichier et appuyer sur Valider</b>`,
        class: 'info',
      };
    }

    if (data.status == 'ERROR') {
      return {
        html: this.processErrorsHTML(data),
        class: 'error',
      };
    }

    if (data.status == 'STARTING') {
      let html = `
      <h4>Import en attente de démarrage</h4>
      `;
      return {
        html,
        class: 'info',
      };
    }

    if (data.status == 'PROCESSING') {
      let steps = Object.values(data['steps']);
      let currentStep = steps[steps.length - 1];
      let html = `
      <h4>Import en cours</h4>
      <p> Étape : ${currentStep}</p>
      `;
      // html += `<p><b>Veuillez appuyer sur valider pour insérer les données</b></p>`;
      return {
        html,
        class: 'info',
      };
    }

    if (data.status == 'PENDING') {
      let html = `
      <h4>Données prêtes pour l'import</h4>
      <p> Ensemble des modifications à venir</p>
      ${this.txtNbLignes(data)}
      `;
      html += `<p><b>Veuillez appuyer sur valider pour insérer les données</b></p>`;
      return {
        html,
        class: 'info',
      };
    }

    if (data.status == 'DONE') {
      let html = `
      <h4>Import Terminé</h4>
      ${this.txtNbLignes(data)}
      `;
      return {
        html,
        class: 'success',
      };
    }

    if (data.status == 'ERROR') {
      return {
        html: `
        <p>${data.errors.length} Erreurs</p>
        <p> Voir les détails dans l'onglet <b>Erreurs</b>
        `,
        class: 'error',
      };
    }
  }

  txtNbLignes(data) {
    let html = '';
    let htmlUpdate = '',
      htmlUnchanged = '';
    let nbChar = Math.max(
      ...Object.values(data.res).map((v) => Math.ceil(v ? Math.log10(Number(v)) : 0)),
    );
    let charSpace = '_';
    let nbRaw = data.res.nb_raw.toString().padStart(nbChar, charSpace);
    let nbProcess = data.res.nb_process.toString().padStart(nbChar, charSpace);
    let nbInsert = data.res.nb_insert.toString().padStart(nbChar, charSpace);
    let nbUpdate = data.res.nb_update.toString().padStart(nbChar, charSpace);
    let nbUnchanged = data.res.nb_unchanged.toString().padStart(nbChar, charSpace);

    if (data.options.enable_update) {
      htmlUpdate += `<li>${nbUpdate} ligne(s) mises à jour</li>`;
    }

    if (data.res.nb_unchanged) {
      htmlUnchanged += `<li>${nbUnchanged} ligne(s) non modifiées</li>`;
    }

    return `<ul>
    <li>${nbRaw} ligne(s) dans le fichier</li>
    <li>${nbProcess} ligne(s) à traiter</li>
    <li>${nbInsert} ligne(s) à insérer</li>
    ${htmlUpdate}
    ${htmlUnchanged}
    </ul>`.replace(/_/g, '&nbsp;');
  }

  // pour l'affichage des erreurs
  processErrorsHTML(data) {
    if (!data.errors?.length) {
      return '';
    }

    let errorHTML = `<h4>${data.errors.length} erreurs</h4>`;

    for (const error of data.errors) {
      const keyTxt =
        error.key && error.relation_key
          ? `<code>${error.relation_key}.${error.key}</code> : `
          : error.key
            ? `<code>${error.key}</code> : `
            : '';
      errorHTML += `<div class="import_error">\n`;
      errorHTML += `<span class="import_error_msg">- ${keyTxt}<b>${error.error_msg}</b></span><br>\n`;
      for (const info of error.error_infos || []) {
        const nbLinesTxt = info.nb_lines > info.lines.length ? `... (${info.nb_lines} lignes)` : '';
        const txtValue = info.value != null ? `<code>${info.value}</code> ` : '';
        let infoHTML = `&nbsp&nbsp- ${txtValue}<i>ligne${
          info.lines.length > 1 ? 's' : ''
        } ${info.lines.join(', ')}${nbLinesTxt}`;
        infoHTML += '</i><br>\n';
        errorHTML += infoHTML;
      }
      errorHTML += '</div>';
    }
    return errorHTML;
  }

  // pour les tests d'affichage (avec erreurs et sans erreur)
  importDataTestError = {
    errors: [
      {
        error_code: 'ERR_IMPORT_INVALID_VALUE_FOR_TYPE',
        error_msg: "'valeur invalide (GEOMETRY)",
        key: 'geom',
        valid_values: null,
        error_infos: [{ value: 'Pointage (2.36781997 49.85916606)', lines: [1], nb_lines: 1 }],
        relation_key: null,
      },

      {
        key: 'id_organism',
        error_msg: 'champs obligatoire',
        error_code: 'ERR_IMPORT_REQUIRED',
        error_infos: [{ lines: [1], nb_lines: 1 }],
        relation_key: 'actors',
        valid_values: null,
      },
      {
        key: 'id_nomenclature_type_actor',
        error_msg: 'pas de correspondance',
        error_code: 'ERR_IMPORT_UNRESOLVED',
        error_infos: [
          { lines: [1, 2], value: 'concessionnaire', nb_lines: 2 },
          { lines: [3], value: 'proprietaire', nb_lines: 1 },
        ],
        relation_key: 'actors',
        valid_values: [
          { label_fr: 'Concessionnaire', cd_nomenclature: 'CON' },
          { label_fr: 'Gestionnaire', cd_nomenclature: 'GES' },
          { label_fr: 'Département', cd_nomenclature: 'DEP' },
          { label_fr: 'Propriétaire', cd_nomenclature: 'PRO' },
          { label_fr: 'Intervenant', cd_nomenclature: 'INT' },
          { label_fr: 'État', cd_nomenclature: 'ETA' },
        ],
      },
    ],

    id_import: 1774,
    res: {
      nb_data: 117,
      nb_process: 117,
      nb_raw: 117,
    },
    status: 'ERROR',
  };

  importDataTest = {
    status: 'DONE',
    res: {
      nb_data: 367,
      nb_insert: 0,
      nb_process: 367,
      nb_raw: 367,
      nb_unchanged: 367,
      nb_update: 0,
    },
    id_import: 1,
    options: {},
  };
}
