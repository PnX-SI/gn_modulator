import { Component, OnInit, Input, Injector } from '@angular/core';
import { ListFormService } from '../../../services/list-form.service';
import { ModulesLayoutComponent } from '../base/layout.component';
import { AbstractControl } from '@angular/forms';

import { debounceTime, distinctUntilChanged, mergeMap } from '@librairies/rxjs/operators';
import { Subject, of, Observable } from '@librairies/rxjs';

import utils from '../../../utils';

@Component({
  selector: 'modules-list-form',
  templateUrl: 'list-form.component.html',
  styleUrls: ['../../base/base.scss', 'list-form.component.scss'],
})
export class ModulesListFormComponent extends ModulesLayoutComponent implements OnInit {
  constructor(
    private _listFormService: ListFormService,
    _injector: Injector,
  ) {
    super(_injector);
    this._name = 'list_form';
    this.bPostComputeLayout = true;
  }

  // la liste
  items: any[] = [];

  // liste de valeurs
  // pour pouvoir les garder en mémoire avec les autocomplete
  valueSave: any[] = [];

  // pour pouvoir filter en local
  itemsSave: any[] = [];

  // nombre d'items
  nbItemsTotal;
  nbItemsFiltered;

  // titre avec nb données (total/filtrée)
  titleWithCount;

  /** fonction de comparaison pour mat-select */
  compareFn = (a, b) => a == b;

  // pour les recheches
  search = '';
  searchSubject: Subject<string>;
  searchSubscription = null;

  // chargement en cours
  isLoading = false;

  // les options
  listFormOptions;

  @Input() formControl: AbstractControl = null;

  postComputeLayout(dataChanged, layoutChanged): void {
    if (layoutChanged) {
      this.processListFormConfig();
    }
  }

  /** process de la configuration du composant */
  processListFormConfig() {
    // options de le layout
    this.listFormOptions = utils.copy(this.computedLayout);

    // module_code depuis le context
    this.listFormOptions.module_code = this.context.module_code;

    // initialisation de la recherche ??
    this.initSearch();

    // chargement des données en cours
    this.isLoading = true;

    // initialisation
    this._listFormService
      .initListForm(this.listFormOptions, this.formControl)
      .pipe(
        mergeMap((infos) => {
          // fonction de comparaison
          this.compareFn = this._listFormService.compareFn(
            this.listFormOptions.return_object,
            this.listFormOptions.value_field_name,
          );

          // la liste
          this.items = infos.items;

          // le nombre d'items
          this.setTitle(infos.total, infos.filtered);

          // pour la recherche en local
          this.itemsSave = utils.copy(infos.items);
          return of(true);
        }),
        mergeMap(() => this.processItemsValue(this.listFormOptions, this.formControl.value)),
      )
      .subscribe(() => {
        // fin du chargement
        this.isLoading = false;
      });
  }

  setTitle(nbItemsTotal, nbItemsFiltered) {
    this.nbItemsFiltered = nbItemsFiltered;
    this.nbItemsTotal = nbItemsTotal;
    const strNbItemsTotal = utils.numberForHuman(this.nbItemsTotal, 1);
    const strNbItemsFiltered = utils.numberForHuman(this.nbItemsFiltered, 1);
    this.titleWithCount =
      this.nbItemsTotal == this.nbItemsFiltered
        ? `${this.computedLayout.title || this.computedLayout.key} (${strNbItemsTotal})`
        : `${
            this.computedLayout.title || this.computedLayout.key
          } (${strNbItemsFiltered}/${strNbItemsTotal})`;
  }

  processItemsValue(options, value) {
    // values :  liste d'id pour les tests
    let values = value;

    // multiple ?
    if (values == null) {
      values = [];
    }

    if (!Array.isArray(values)) {
      values = [values];
    }

    // renvoie un objet ??
    if (options.return_object) {
      values = values.map((v) => v[options.value_field_name]);
    }

    // si values == []
    if (values.length == 0) {
      this.valueSave = [];
      return of(true);
    }

    // recherche de values dans la liste (items)
    const missingValuesInItems = values.filter((v) =>
      this.items.every((i) => i[options.value_field_name] != v),
    );

    // les valeur sont trouvées dans la liste
    // ok retour
    if (missingValuesInItems.length == 0) {
      this.valueSave = this.items.filter((i) =>
        values.some((v) => i[options.value_field_name] == v),
      );
      return of(true);
    }

    // sinon
    // - si non autocomplete => pb
    if (missingValuesInItems.length > 0 && !options.reload_on_search) {
      console.error(
        `La ou les valeurs ${missingValuesInItems
          .map((m) => m[options.value_field_name])
          .join(', ')} ne sont pas présentes dans la liste`,
      );
      return of(false);
    }

    // on a des valeurs manquantes (missingValuesInItems) est ce qu'elles sont dans valueSave ?
    let missingValuesInValueSave: any[] = [];
    for (const v of missingValuesInItems) {
      const item = this.valueSave.find((i) => i[options.value_field_name] == v);
      if (!item) {
        missingValuesInValueSave.push(v);
      } else {
        this.items.push(item);
      }
    }

    if (missingValuesInValueSave.length == 0) {
      this.valueSave = this.items.filter((i) =>
        values.some((v) => i[options.value_field_name] == v),
      );
      return of(true);
    }

    // s'il y des valeurs manquante, alors ou va les cherche avec l'api
    return this._listFormService.getMissingValues(missingValuesInValueSave, options).pipe(
      mergeMap((items) => {
        for (let item of items) {
          this.items.push(item);
          this.valueSave.push(item);
        }
        return of(true);
      }),
    );
  }

  // pour la recherche
  initSearch() {
    // sujet
    this.searchSubject = this.searchSubject || new Subject();

    // unsubscribe si besoin
    this.searchSubscription && this.searchSubscription.unsubscribe();

    // debounce time dans le cas autocomplete (reload on search)
    const dt = this.listFormOptions.reload_on_search ? 400 : 0;

    this.searchSubscription = this.searchSubject
      .pipe(distinctUntilChanged(), debounceTime(dt))
      .subscribe((search) => {
        this.processSearchChanged(search);
      });
  }

  /** action lorsque le champs de recherche change */
  searchChanged(event) {
    this.searchSubject.next(event);
  }

  /** processus de recherche dans les items */
  processSearchChanged(search) {
    // recherche "server side"
    // - appel de l'api avec des parametre de filtre
    if (this.listFormOptions.reload_on_search) {
      this.remoteSearch(search);
      // recherche locale
      // - filtrage de la liste selon la valeur de search
    } else {
      this.items = this.localSearch(search);
      this.setTitle(this.itemsSave.length, this.items.length);
    }
  }

  /** Server Side Search */
  remoteSearch(search) {
    // option de recherhe
    this.listFormOptions.search = search;

    // chargement en cours
    this.isLoading = true;

    // appel de l'api
    // on prend en compte les valeurs courrantes
    this._listFormService
      .getSelectList(this.listFormOptions, this.formControl.value)
      .pipe(
        mergeMap((infos) => {
          this.items = infos.items;
          this.setTitle(infos.total, infos.filtered);
          return this.processItemsValue(this.listFormOptions, this.formControl.value);
        }),
      )
      .subscribe(() => {
        this.isLoading = false;
      });
  }

  /** Local search */
  localSearch(search) {
    // si search est null ou ''
    // -> on renvoie toute la liste (itemsSave)
    if ([null, undefined, ''].includes(search)) {
      return this.itemsSave;
    }

    // on recherche sans prendre en compte la casse ou les accents
    // -> on tranforme search
    const searchLowerUnaccent = utils.lowerUnaccent(search);

    // filtrage selon searchLowerUnaccent
    return this.itemsSave.filter((item) => {
      let label = item[this.listFormOptions.label_field_name];

      // on ne tient pas compte de la casse et des accents
      label = utils.lowerUnaccent(item[this.listFormOptions.label_field_name]);

      // si label contient searchLowerUnaccent
      // -> il est dans la liste
      return label.includes(searchLowerUnaccent);
    });
  }

  /** remise à zéro de la selection
   * - action pour le boutton 'clear'
   */
  clearSelection(event) {
    // ne pas propager l'action
    // sinon on a des comportements bizzare (validation du formulaire ou autre)
    event.stopPropagation();

    // prise en compte de l'option multiple
    const value = this.listFormOptions.multiple ? [] : null;

    // on donne la valeur de value au formulaire
    this.formControl.patchValue(value);
  }

  /** Action quand l'input du select est modifié
   * si une fonction change est définie dans les options
   */
  inputChange() {
    this.listFormOptions.change && this.listFormOptions.change();
  }
}
