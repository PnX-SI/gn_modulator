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
          Veuillez choisir un fichier et appuyer sur Valider`,
        class: 'info',
      };
    }

    if (data.status == 'READY') {
      return {
        html: `
          <p>- Nombre de lignes ${data.res.nb_raw}</p>
          <p>- Nombre d'insertion ${data.res.nb_insert}</p>
          <p>- Nombre de mise à jour ${data.res.nb_update} ${
          data.options.enable_update ? '' : '(MAJ Non autorisée)'
        }</p>
          Veuillez appuyer sur valider pour insérer les données`,
        class: 'info',
      };
    }

    if (data.status == 'DONE') {
      return {
        html: `
          Import Terminé
          `,
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

  // for (let error of impt.errors.filter((e) => e.code == 'ERR_IMPORT_REQUIRED')) {
  //   if (!txtErrorRequired) {
  //     txtErrorRequired = `<h5></h5>`;
  //   }
  //   txtErrorRequired += `<b>${error.key}</b> ${error.lines.length} ligne(s): [${error.lines}]<br>`;
  // }
  // if (txtErrorRequired) {
  //   txtImport += '<hr>';
  //   txtImport += txtErrorRequired;
  // }

  // let txtErrorUnresolved;
  // for (let error of impt.errors.filter((e) => e.code == 'ERR_IMPORT_UNRESOLVED')) {
  //   if (!txtErrorUnresolved) {
  //     txtErrorUnresolved = `<h5>Champs non résolus</h5>`;
  //   }
  //   txtErrorUnresolved += `<b>${error.key}</b> ${error.lines.length} ligne(s): [${error.lines}]<br>`;
  //   if (error.values) {
  //     txtErrorUnresolved += `Valeurs parmi : ${error.values
  //       .map((v) => v.cd_nomenclature)
  //       .join(', ')}<br>`;
  //   }
  // }
  // if (txtErrorUnresolved) {
  //   txtImport += '<hr>';
  //   txtImport += txtErrorUnresolved;
  // }

  // for (let error of impt.errors.filter(
  //   (e) => !['ERR_IMPORT_REQUIRED', 'ERR_IMPORT_UNRESOLVED'].includes(e.code)
  // )) {
  //   txtImport += '<hr>';
  //   txtImport += `${error.code}: ${error.msg}`;
  // }

  // return txtImport;
  // }
}
