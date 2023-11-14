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

  importRequest(moduleCode, object_code, data, params = {}) {
    return this._mRequest.postRequestWithFormData(
      `${this._mConfig.backendModuleUrl()}/import_async/${moduleCode}/${object_code}/${
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

  processErrorsLine(data) {
    if (!data.errors?.length) {
      return '';
    }

    const lines = {};
    for (const error of data.errors) {
      for (const line of error.lines || []) {
        lines[line] = lines[line] || {};
        lines[line][error.error_code] = lines[line][error.error_code] || {
          error_msg: error.error_msg,
          keys: [],
        };
        lines[line][error.error_code].keys.push(error.key);
      }
    }
    let errorHTML = `<h4>${Object.keys(lines).length} ligne${
      Object.keys(lines).length > 1 ? 's' : ''
    } en erreur</h4>`;

    for (const line of Object.keys(lines)
      .map((l) => parseInt(l))
      .sort()) {
      errorHTML += `- <b>${line}</b><br>`;
      for (const errorCode of Object.keys(lines[line]).sort()) {
        errorHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${lines[line][errorCode].error_msg}:<br>`;
        errorHTML += `&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>${lines[line][errorCode].keys.join(
          ', ',
        )}</i><br>`;
      }
    }
    return errorHTML;
  }

  processErrorsType(data) {
    if (!data.errors?.length) {
      return '';
    }

    let errorHTML = `<h4>${data.errors.length} erreurs</h4>`;

    const errors = {};
    for (const error of data.errors) {
      errors[error.error_code] = errors[error.error_code] || { error_msg: error.error_msg };
    }

    for (const errorType of Object.keys(errors)) {
      const errorsOfType = data.errors.filter((e) => e.error_code == errorType);
      errorHTML += `<h5>${errorsOfType[0].error_msg}</h5>`;
      errors[errorType].keys = {};
      for (let error of errorsOfType) {
        if (error.key) {
          errors[errorType].keys[error.key] = { lines: error.lines };

          for (const [i, line] of error.lines.entries()) {
            errorHTML += `- [ligne ${line}] : ${error.error_values[i]}<br>`;
          }
        }
      }
    }
    return errorHTML;
  }
}
