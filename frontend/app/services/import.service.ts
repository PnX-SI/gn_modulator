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
      `${this._mConfig.backendModuleUrl()}/import/${moduleCode}/${object_code}/${
        data.id_import || ''
      }`,
      {
        data: data.id_import ? {} : data,
        params,
      }
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

    if (data.status == 'READY') {
      let html = `
      <h4>Données prêtes pour l'import</h4>
      <p>- Nombre de lignes <b>${data.res.nb_raw}</b></p>
      <p>- Nombre d'insertion <b>${data.res.nb_insert}</b></p>`;
      if (data.options.enable_update && data.res.nb_update) {
        html += `<p>- Nombre de mise à jour <b>${data.res.nb_update}</b></p>`;
      }
      if (!data.options.enable_update && data.res.nb_update) {
        html += `<p>- <span style="text-decoration:line-through"> Nombre de mise à jour ${data.res.nb_update} </span>(MAJ Non autorisée)</p>`;
      }
      html += `<p><b>Veuillez appuyer sur valider pour insérer les données</b></p>`;
      return {
        html,
        class: 'info',
      };
    }

    if (data.status == 'DONE') {
      let html = `
      <h4>Import Terminé</h4>
      <p>- Nombre de lignes ${data.res.nb_raw}</p>
      <p>- Nombre d'insertion ${data.res.nb_insert}</p>
      `;
      if (data.options.enable_update) {
        html += `<p>- Nombre de mise à jour ${data.res.nb_update}</p>`;
      }
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

  processErrorsLine(data) {
    if (!data.errors?.length) {
      return '';
    }

    const lines = {};
    for (const error of data.errors) {
      for (const line of error.lines) {
        lines[line] = lines[line] || {};
        lines[line][error.code] = lines[line][error.code] || { msg: error.msg, keys: [] };
        lines[line][error.code].keys.push(error.key);
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
        errorHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${lines[line][errorCode].msg}:<br>`;
        errorHTML += `&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>${lines[line][errorCode].keys.join(
          ', '
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
      errors[error.code] = errors[error.code] || { msg: error.msg };
    }

    for (const errorType of Object.keys(errors)) {
      const errorsOfType = data.errors.filter((e) => e.code == errorType);
      errorHTML += `<h5>${errorsOfType[0].msg}</h5>`;
      errors[errorType].keys = {};
      for (let error of errorsOfType) {
        if (error.key) {
          errors[errorType].keys[error.key] = { lines: error.lines };
          errorHTML += `- ${error.key} : ligne${
            error.lines.length > 1 ? 's' : ''
          } ${error.lines.join(', ')}<br>`;
        }
      }
    }
    return errorHTML;
  }
}
