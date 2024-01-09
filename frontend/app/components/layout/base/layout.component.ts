import {
  Component,
  OnInit,
  Input,
  SimpleChanges,
  EventEmitter,
  Output,
  Injector,
} from '@angular/core';
import { ModulesConfigService } from '../../../services/config.service';
import { ModulesLayoutService } from '../../../services/layout.service';
import { ModulesContextService } from '../../../services/context.service';
import { ModulesFormService } from '../../../services/form.service';
import { ModulesActionService } from '../../../services/action.service';
import { ModulesObjectService } from '../../../services/object.service';
import { Subject } from '@librairies/rxjs';

import { debounceTime } from '@librairies/rxjs/operators';

import utils from '../../../utils';

/** Composant de base pour les layouts */
@Component({
  selector: 'modules-layout',
  templateUrl: 'layout.component.html',
  styleUrls: ['../../base/base.scss', 'layout.component.scss'],
})
export class ModulesLayoutComponent implements OnInit {
  /** données */
  @Input() debug: any;

  /** agencement */
  @Input() layout: any;

  /** données */
  @Input() data: any;
  localData: any;

  /** actions */
  @Output() onAction = new EventEmitter<any>();

  // disposition verticale (par défaut) ou horizontale (si direction='row') des items
  @Input() direction: string;

  // pour faire passer des infos aux composants enfants ?
  @Input() parentContext: any = {};
  context: any = {};

  // si processing ( par ex: affichage de spinner)
  @Input() isProcessing;

  // layout calculé (en fonction de data et autres)
  computedLayout: any;

  // données et layout calculé sauvegardé
  // (pour ne pas déclencher postComputeLayout s'il n'y a pas besoin)
  computedLayoutSave: any;
  dataSave: any;
  contextSave: any;

  bPostComputeLayout; // pour ne pas avoir tojours à comparer dataSave/data computedLayoutSave/computedLayout
  bCheckParentsHeight;
  $parentsHeight;

  // layout récupéré depuis layoutCode
  // TODO à gérer overen backend ?
  layoutFromCode;

  /** margin for debug display
   * help with debugging nested layout
   */

  /** Type de layout
   */
  layoutType: string;

  /** pour l'affichage du debug */
  debugData;
  isDebugAllowed = false;

  // données associées à layout.key
  elementData;
  elementKey;

  formControl;
  localFormGroup;

  // nom du composant (pour le debug)
  _name: string;

  // id du composant (random)
  // - pour le style
  // - pour les carte ?
  _id;

  // composant initialisé (pour l'affichage)
  isInitialized = false;

  // composant destroyed
  isDestroyed = false;

  // services
  _mConfig: ModulesConfigService;
  _mAction: ModulesActionService;
  _mLayout: ModulesLayoutService;
  _mContext: ModulesContextService;
  _mForm: ModulesFormService;
  _mObject: ModulesObjectService;

  // pour les éléments avec overflow = true
  parentResizeObserver;
  parentsElement;
  heightOverflowSave;

  // height auto
  docHeightSave;

  // listenPage resize
  bListenPageResize;

  assertionIsTrue;

  computedItems;
  itemsContext;

  // for tabs
  selectedIndex;

  actionProcessing; // pour les spinners

  utils; // pour acceder à utils dans les templates

  _subs = {};

  constructor(protected _injector: Injector) {
    this._name = 'layout';
    this._id = Math.round(Math.random() * 1e10);
    this._mLayout = _injector.get(ModulesLayoutService);
    this._mContext = _injector.get(ModulesContextService);
    this._mForm = _injector.get(ModulesFormService);
    this._mConfig = _injector.get(ModulesConfigService);
    this._mObject = _injector.get(ModulesObjectService);
    this._mAction = this._injector.get(ModulesActionService);
    this.utils = utils;
  }

  ngOnInit() {
    // initialisation du layout
    this.processLayout();

    // subscription pour recalculer le layout
    this._subs['reComputeLayout'] = this._mLayout.$reComputeLayout
      .pipe(debounceTime(50))
      .subscribe(() => {
        this.computeLayout();
      });

    this._subs['refreshData'] = this._mLayout.$refreshData.subscribe((objectCode) => {
      this.refreshData(objectCode);
    });

    this._subs['redrawElem'] = this._mLayout.$reDrawElem.subscribe(() => {
      this.onRedrawElem();
    });

    this._mLayout.$stopActionProcessing.subscribe(() => {
      this.actionProcessing = false;
    });

    // lorque une postInitialisation est nécessaire
    this.postInit();
    this.isDebugAllowed = this._mObject.hasPermission('MODULATOR', 'ADMIN', 'R');
  }

  onRedrawElem() {}

  // à redefinir pour faire une action apres init
  postInit() {}

  // pour les logs avec info sur _name, type, id
  log(...args) {
    console.log(this._name, this.layout && this.layout.type, this._id, ...args);
  }

  // à redéfinir pour effectuer des actions apres computedLayout
  postComputeLayout(dataChanged, layoutChanged, contextChanged) {}

  // appelé à l'initiation ( ou en cas de changement de data/layout/globalData)
  processLayout() {
    // calcul de computedLayout
    this.computeLayout();
    this.assertionIsTrue = utils.fastDeepEqual(
      this.computedLayout?.test,
      this.computedLayout?.test_value,
    );
    // à redéfinir
    this.postProcessLayout();

    // resize ?
    this.listenPageResize();

    // le composant est initialisé
    this.isInitialized = true;
  }

  getLocalData() {
    return this._mLayout.getLocalData({
      data: this.data,
      context: this.context,
      layout: this.layout,
    });
  }

  processContext() {
    // passage de parentContext (venant des layout parentsElement) à context (à destination des enfants)
    // copie

    // à clarifier

    if (!this.parentContext) {
      return;
    }

    const layout = this.computedLayout || this.layout;

    if (!layout) return;

    for (const key of [
      'debug',
      'appearance',
      'index',
      'map_id',
      'map_params',
      'skip_required',
      'hidden_options',
    ]) {
      if (this.parentContext[key] != null || layout[key] != null) {
        this.context[key] = layout[key] == null ? this.parentContext[key] : layout[key];
      }
    }

    if (this._name != 'form') {
      this.context['form_group_id'] = this.parentContext['form_group_id'];
    }

    if (this.debug !== undefined) {
      this.context.debug = this.debug ? 1 : 0;
    }

    if (this.parentContext.debug) {
      this.context.debug = this.parentContext.debug + 1;
    }
    // dataKeys

    this.context.data_keys = utils.copy(this.parentContext.data_keys) || [];
    this.preProcessContext();

    this.localData = this.getLocalData();

    // ? layout ou computedLayout
    const computedContext = this._mContext.getContext({
      layout,
      context: this.parentContext,
    });

    this.context.module_code = computedContext.module_code;
    this.context.object_code = computedContext.object_code;
    this.context.page_code = computedContext.page_code;
    this.context.params = computedContext.params;
    this.context.current_user = computedContext.current_user;

    const objectConfig = this.objectConfig() || {};
    if (
      this.parentContext.object_code &&
      this.context.object_code == this.parentContext.object_code
    ) {
      for (const key of ['filters', 'prefilters', 'value', 'nb_filtered', 'nb_total']) {
        this.context[key] = layout[key] || this.parentContext[key] || objectConfig[key];
      }
    }

    this.postProcessContext();

    // ici pour filter value, etc....
    // 1 depuis moduleConfig
    // 2 depuis context
    // 3 depuis layout
  }

  objectConfig() {
    return this._mObject.objectConfigContext(this.context);
  }

  /**
   * A redéfinir dans les composants
   * pour les besoins spécifiques
   * - data_keys etc...
   **/
  postProcessContext() {}

  preProcessContext() {}

  processElementData() {
    if (!(this.computedLayout && this.context.data_keys)) {
      return;
    }

    if (this.computedLayout.key) {
      this.elementKey = [...this.context.data_keys, this.computedLayout.key].join('.');
      this.elementData = utils.getAttr(this.localData, this.computedLayout.key);
    } else {
      this.elementData = this.localData;
      this.elementKey = this.context.data_keys.join('.');
    }

    if (this.computedLayout.type == 'date' && this.elementData) {
      this.elementData = this.elementData.split('-').reverse().join('/');
    }

    if (this._name == 'layout-element' && Array.isArray(this.elementData)) {
      this.elementData = this.elementData.join(', ');
    }
  }

  processFormControl() {
    if (!(this.computedLayout && this.context.form_group_id)) {
      return null;
    }
    this.localFormGroup = this._mForm.getFormControl(
      this.context.form_group_id,
      this.context.data_keys,
    );
    this.formControl = this._mForm.getFormControl(this.localFormGroup, this.computedLayout.key);
  }

  // calcul de computedLayout
  // pour prendre en compte les paramètre qui sont des functions
  computeLayout() {
    // calcul du type de layout
    this.layoutType = this.layoutType || this._mLayout.getLayoutType(this.layout);

    this.processContext();

    // calcul du layout
    this.computedLayout = this._mLayout.computeLayout({
      layout: this.layout,
      data: this.data,
      context: this.context,
    });

    // besoin de maj apres pour les données object ?
    // récupération des données associées à this.computedLayout.key

    for (const key of ['filters', 'prefilters', 'value', 'nb_filtered', 'nb_total']) {
      const computedValue = this.computedLayout && this.computedLayout[key];
      this.context[key] = computedValue != null ? computedValue : this.context[key];
    }

    if (this.context.form_group_id) {
      this.processFormControl();
    }

    this.processElementData();

    this.processDebugData();

    // }

    if (!this.computedLayout) {
      return;
    }

    this.processItems();

    // options layout

    // si layout_code est défini
    // on va chercher le layout correspondant dans la config
    if (this.computedLayout.code && !this.layoutFromCode) {
      const contextTemplateDefault = this._mContext.config;
      const templateParams = {
        ...(contextTemplateDefault || {}),
        ...(this.computedLayout.template_params || {}),
      };
      let layoutFromCode = this._mLayout.getLayoutFromCode(
        this.computedLayout.code,
        templateParams,
      );

      this.layoutFromCode = layoutFromCode.layout;
    }

    if (this.computedLayout.overflow) {
      this.bCheckParentsHeight = true;
    }

    if (this.bCheckParentsHeight) {
      this.initCheckParentsHeight();
    }

    /** pour éviter de déclencher postComputeLayout s'il n'y a pas de changmeent effectif */
    if (!this.bPostComputeLayout) {
      return;
    }

    // comparaison entre le layout calculé et les données précédentes
    const dataCopy = utils.copy(this.data);
    const computedLayoutCopy = utils.copy(this.computedLayout);
    const contextCopy = utils.copy(this.context);

    const dataChanged = !utils.fastDeepEqual(this.dataSave, dataCopy);
    const layoutChanged = !utils.fastDeepEqual(this.computedLayoutSave, computedLayoutCopy);
    const contextChanged = !utils.fastDeepEqual(this.contextSave, contextCopy);

    if (
      this.computedLayoutSave &&
      this.dataSave &&
      this.contextSave &&
      !layoutChanged &&
      !dataChanged &&
      !contextChanged
    ) {
      return;
    }

    this.postComputeLayout(dataChanged, layoutChanged, contextChanged);

    // sauvegarde des données pour la prochaine comparaison
    this.dataSave = dataCopy;
    this.computedLayoutSave = computedLayoutCopy;
    this.contextSave = contextCopy;
  }

  initCheckParentsHeight() {
    const elem = document.getElementById(this._id);
    if (!elem || this.parentResizeObserver) {
      return;
    }
    this.$parentsHeight = new Subject();
    this.$parentsHeight.pipe(debounceTime(50)).subscribe(() => {
      this.processParentsHeightChange();
    });
    this.parentResizeObserver = new ResizeObserver(() => this.$parentsHeight.next(true));

    this.parentsElement = [];
    let p = elem.parentElement?.closest('div.layout-item');

    while (p) {
      // this.parentsElement.push(p.id as never);
      this.parentsElement.push(p as never);
      p = p.parentElement?.closest('div.layout-item');
    }
    this.parentResizeObserver.observe(...this.parentsElement, document.body);
    this.$parentsHeight.next(true);
    window.addEventListener('resize', () => this.$parentsHeight.next(true));
  }

  processParentsHeightChange() {
    if (this.context.debug) {
      return;
    }
    if (this.computedLayout.overflow) {
      // setTimeout(() => {
      this.processHeightOverflow();
      // });
    }
    this.customParentsHeightChange();
  }

  customParentsHeightChange() {}

  // pour gérer les composant avec overflow = true
  processHeightOverflow() {
    const condNothing =
      this.heightOverflowSave &&
      this.docHeightSave &&
      document.body.clientHeight == this.docHeightSave &&
      document.body.clientHeight == this.docHeightSave;

    if (condNothing) {
      return;
    }

    const condUp =
      !(this.heightOverflowSave && this.docHeightSave) ||
      document.body.clientHeight < this.docHeightSave ||
      this.parentsElement[0].clientHeight < this.heightOverflowSave;

    let direction = condUp ? 'up' : 'down';

    if (direction == 'up') {
      this.setStyleOverFlow();
      setTimeout(() => {
        this.setStyleOverFlow(this.parentsElement[0].clientHeight);
      }, 10);
    } else if (direction == 'down') {
      this.setStyleOverFlow(this.parentsElement[0].clientHeight);
    }
  }

  setStyleOverFlow(height: any = null) {
    let styleHeight;
    const isTabs = this.computedLayout.display == 'tabs';
    if (!height) {
      styleHeight = 50;
    } else {
      this.heightOverflowSave = height;
      this.docHeightSave = document.body.clientHeight;
      // styleHeight = isTabs ? height - 50 : height;
      styleHeight = isTabs ? height - 65 : height;
    }

    // styleHeight = 50
    const style = {};

    style['height'] = `${styleHeight}px`;
    // style['background-color'] = 'red';
    if (!isTabs) {
      style['overflow-y'] = 'scroll';
    }

    const layoutStyleKey = isTabs ? 'style_tab' : 'style';

    this.layout[layoutStyleKey] = {
      ...(this.layout[layoutStyleKey] || {}),
      ...style,
    };
    this.computedLayout[layoutStyleKey] = {
      ...(this.computedLayout[layoutStyleKey] || {}),
      ...style,
    };
  }

  /**
   * Pour gérer les élément dont on souhaite que la taille correspondent à la taille de la fenètre
   */
  listenPageResize() {
    // pour les composant avec computedLayout.height_auto
    if (!this.computedLayout?.height_auto) {
      return;
    }

    // pour ne faire appel qu'une seule fois à la fonction
    // on utilise bListenPageResize
    if (this.bListenPageResize) {
      return;
    }

    this.bListenPageResize = true;

    // on attend l'element html pour lui donner la taille de la page
    utils.waitForElement(this._id).then((elem) => {
      this.processHeightAuto();
      // on ajoute un évènement en cas de changement de la hauteur de la fenêtre
      window.addEventListener(
        'resize',
        (event) => {
          this.processHeightAuto();
        },
        true,
      );
    });
  }

  // action quand la taille change

  /** pour mettre les layout avec height_auto = true à la hauteur totale de la page */
  processHeightAuto() {
    if (!this.computedLayout.height_auto) {
      return;
    }

    const elem = document.getElementById(this._id);
    if (!elem) {
      return;
    }
    const elementHeight = elem && `${elem.clientHeight}px`;
    const bodyHeight = `${document.body.clientHeight - elem.offsetTop - 4}px`;

    // si la taille de l'élément correspond à la taille de la page
    // -> on ne fait rien

    if (elementHeight == bodyHeight && this.computedLayout.style?.height == bodyHeight) {
      return;
    }

    this.computedLayout.style = this.computedLayout.style || {};
    this.computedLayout.style.height = bodyHeight;

    this.layout.style = this.layout.style || {};
    this.layout.style.height = bodyHeight;
  }

  // a redefinir pour faire des actions après processLayout
  postProcessLayout() {}

  emitAction(event) {
    this.onAction.emit(event);
  }

  /** pour les bouttons
   * quand layout.action est defini
   */
  onButtonClick(event) {
    if (this.computedLayout.click) {
      this.computedLayout.click(event);
      return;
    }

    const action = this.computedLayout.action;
    if (!action) {
      return;
    }

    // open modal TODO subject ?
    if (action.modal_name) {
      this._mLayout.openModal(action.modal_name, this.data);
      return;
    }

    if (action == 'close') {
      this._mLayout.closeModals();
      return;
    }

    this.actionProcessing = true;
    this.onAction.emit({
      action: this.layout.action,
      data: this.data,
      layout: this.computedLayout,
      context: this.context,
    });
  }

  processAction(event) {
    this.emitAction(event);
  }

  processDebugData() {
    if (!(this.layout && this.isDebugAllowed)) {
      return;
    }

    const elementDataDebug = this.elementData;
    const localDataDebug = this.localData;

    const contextDebug = { ...this.context };
    delete contextDebug.current_user;

    const prettyLayout = this.prettyTitleObjForDebug('layout', this.layout);
    const prettyComputedLayout = this.prettyTitleObjForDebug(
      'computed layout',
      this.computedLayout,
    );
    const prettyData = this.prettyTitleObjForDebug('data', this.data);
    const prettyLocalData = this.prettyTitleObjForDebug(
      `local data (${this.context.data_keys?.join('.')})`,
      localDataDebug,
    );
    const prettyElementData = this.prettyTitleObjForDebug(
      `element data (${this.elementKey})`,
      elementDataDebug,
    );
    const prettyContext = this.prettyTitleObjForDebug('context', contextDebug);

    this.debugData = {
      code: this.computedLayout.code,
      layout: prettyLayout,
      computedLayout: prettyComputedLayout,
      data: prettyData,
      local_data: !utils.fastDeepEqual(this.localData, this.data) && prettyLocalData,
      element_data: !utils.fastDeepEqual(this.elementData, this.localData) && prettyElementData,
      context: prettyContext,
      debug: this.context.debug,
      itemsLength: this.layout.items?.length,
      layoutType: this.layoutType,
      direction: this.computedLayout.direction,
      display: this.computedLayout.display,
    };
  }

  prettyTitleObjForDebug(title, obj) {
    // let srtPretty = `${title}\n\n${JSON.stringify(obj, null, '____  ')}`
    let srtPretty = `${title}\n\n${utils.YML.dump(obj, { skipInvalid: true }).replaceAll(
      ' ',
      '_',
    )}`;
    return srtPretty;
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {
      if (utils.fastDeepEqual(change['currentValue'], change['previousValue'])) {
        continue;
      }

      if (['layout', 'data', 'parentContext', 'debug'].includes(key)) {
        this.processLayout();
      }
    }
  }

  onTabChanged($event) {
    this._mLayout.reDrawElem('tab changed');
  }

  moduleCode() {
    return this.context.module_code;
  }

  objectCode() {
    return this.context.object_code;
  }

  moduleConfig() {
    return this._mConfig.moduleConfig(this.moduleCode());
  }

  refreshData(objectCode) {}

  checkObjectPermission(context) {
    const objectConfig = this._mObject.objectConfigContext(context);
    if (objectConfig.permission_object_code || objectConfig.module_code) {
      const permissionModuleCode = objectConfig.module_code || this.context.module_code;
      const permissionObjectCode = objectConfig.permission_object_code || 'ALL';
      const res = this._mObject.hasPermission(permissionModuleCode, permissionObjectCode, 'R');
      return res;
    }
    return true;
  }

  processItems() {
    const items = this.layoutType == 'items' ? this.layout : this.layout.items || [];

    this.computedItems = items.map
      ? items.map((item) => {
          if (!utils.isObject(item)) {
            return item;
          }
          const computedItem = {};
          const itemContext = {
            ...this.context,
            object_code: item.object_code || this.context.object_code,
            module_code: item.module_code || this.context.module_code,
          };
          for (const key of ['label', 'hidden', 'disabled', 'lazy_loading']) {
            computedItem[key] = this._mLayout.evalLayoutElement({
              element: item[key],
              layout: item,
              data: this.data,
              context: itemContext,
            });
          }
          // checkItemPermission
          if (item.object_code && !this.checkObjectPermission(itemContext)) {
            computedItem['hidden'] = true;
          }
          return computedItem;
        })
      : [];

    // pour les tabs
    // - si computedLayout.tab
    //    alors on choisi cet onglet par defaut
    setTimeout(() => {
      if (this.computedLayout.display == 'tabs' && this.computedLayout.selected_tab) {
        this.selectedIndex = this.computedItems.findIndex(
          (i) => i.label == this.computedLayout.selected_tab,
        );
      }
    }, 100);
  }

  onDestroy() {}

  ngOnDestroy() {
    this.isDestroyed = true;
    for (const [subKey, sub] of Object.entries(this._subs)) {
      sub && (sub as any).unsubscribe();
    }
    this.onDestroy();
  }
}
