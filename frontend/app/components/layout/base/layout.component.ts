import {
  Component,
  OnInit,
  Input,
  SimpleChanges,
  EventEmitter,
  Output,
  Injector,
} from "@angular/core";
import { ModulesLayoutService } from "../../../services/layout.service";
import utils from "../../../utils";

/** Composant de base pour les layouts */
@Component({
  selector: "modules-layout",
  templateUrl: "layout.component.html",
  styleUrls: ["../../base/base.scss", "layout.component.scss"],
})
export class ModulesLayoutComponent implements OnInit {
  // @Output() layoutChange = new EventEmitter<any>();

  // @Input() layoutDefinition: any;

  /** agencement */
  @Input() layout: any;

  /** données */
  @Input() data: any;
  @Input() globalData: any;

  /** actions */
  @Output() onAction = new EventEmitter<any>();

  /** debug */
  @Input() debug: any;

  /** debug */
  @Input() depth = 0;

  // disposition verticale (par défaut) ou horizontale (si direction='row') des items
  @Input() direction: string;

  // TODO
  // pour les formulaires, faire passer le formGroup (TODO par un service ?)
  @Input() options: any = {};

  // si processing ( par ex: affichage de spinner)
  @Input() isProcessing;

  // layout calculé (en fonction de data et autres)
  computedLayout: any;

  // données et layout calculé sauvegardé
  // (pour ne pas déclencher postComputeLayout s'il n'y a pas besoin)
  computedLayoutSave: any;
  dataSave: any;
  bPostComputeLayout; // pour ne pas avoir tojours à comparer dataSave/data computedLayoutSave/computedLayout

  // layout récupéré depuis layoutName
  // TODO à gérer en backend ?
  layoutFromName;

  /** margin for debug display
   * help with debugging nested layout
   */
  debugMarginLeft = "0px";

  /** Type de layout
   */
  layoutType: string;

  /** pour l'affichage du debug */
  prettyDebug;

  // données associées à layout.key
  dataKey;

  // nom du composant (pour le debug)
  _name: string;

  // id du composant (random)
  // - pour le style
  // - pour les carte ?
  _id;

  // composant initialisé (pour l'affichage)
  isInitialized = false;

  // services
  _mLayout: ModulesLayoutService;

  // pour les éléments avec overflow = true
  docHeightSave;

  // listenPage resize
  bListenPageResize;

  computedItems;

  actionProcessing; // pour les spinners
  
  utils; // pour acceder à utils dans les templates
  
  constructor(protected _injector: Injector) {
    this._name = "layout";
    this._id = Math.round(Math.random() * 1e10);
    this._mLayout = _injector.get(ModulesLayoutService);
    this.utils = utils;
  }

  ngOnInit() {
    // initialisation du layout
    this.processLayout();

    // subscription pour recalculer le layout
    this._mLayout.$reComputeLayout.subscribe(() => {
      this.computeLayout();
    });

    this._mLayout.$refreshData.subscribe((objectName) => {
      this.refreshData(objectName);
    });
    
    this._mLayout.$reComputedHeight.subscribe(() => {
      this.onHeightChange();
    });

    this._mLayout.$reDrawElem.subscribe(() => {
      this.onRedrawElem();
    });

    this._mLayout.$stopActionProcessing.subscribe(() => {
      this.actionProcessing = false;
    });

    
    // pour les élément avec heigh_auto = true
    // this.listenPageResize();

    // lorque une postInitialisation est nécessaire
    this.postInit();
  }

  onRedrawElem() {};

  // à redefinir pour faire une action apres init
  postInit() {}

  // pour les logs avec info sur _name, type, id
  log(...args) {
    console.log(this._name, this.layout && this.layout.type, this._id, ...args);
  }

  // idem que log mais seulement quand debug = true
  debugLog(...args) {
    this.debug && this.log(...args);
  }

  // pour récupérer formGroup depuis les options
  getFormGroup() {
    return this.options.formGroup;
  }

  // à redéfinir pour effectuer des actions apres computedLayout
  postComputeLayout(dataChanged, layoutChanged) {}

  // appelé à l'initiation ( ou en cas de changement de data/layout/globalData)
  processLayout() {
    this.globalData = this.globalData || this.data;
    // calcul de computedLayout
    this.computeLayout();
    // à redéfinir
    this.postProcessLayout();

    // resize ?
    this.listenPageResize();

    // le composant est initialisé
    this.isInitialized = true;
  }

  // calcul de computedLayout
  // pour prendre en compte les paramètre qui sont des functions
  computeLayout() {
    // calcul du type de layout
    this.layoutType =
      this.layoutType || this._mLayout.getLayoutType(this.layout);

    // calcul du layout
    this.computedLayout = this._mLayout.computeLayout({
      layout: this.layout,
      data: this.data,
      globalData: this.globalData,
      formGroup: this.getFormGroup(),
    });

    // récupération des données associées à this.computedLayout.key
    this.dataKey =
      this.layoutType == "key"
        ? utils.getAttr(this.data, this.computedLayout.key)
        : this.data;

    // pour l'affichage du debug
    // if (this.debug) {
    this.prettyDebug = {
      layout: this.pretty(this.computedLayout),
      data: this.pretty(this.data),
      dataKey: this.pretty(this.dataKey),
    };
    // }

    if (!this.computedLayout) {
      return;
    }

    const items =
      this.layoutType == "items" ? this.layout : this.layout.items || [];

    this.computedItems = items.map
      ? items.map((item) =>
          this._mLayout.computeLayout({
            layout: item,
            data: this.data,
            globalData: this.globalData,
            formGroup: this.getFormGroup(),
          })
        )
      : [];

    // si layout_name est défini
    // on va chercher le layout correspondant dans la config
    // TODO (gérer ça en backend)
    if (this.computedLayout.layout_name && !this.layoutFromName) {
      const layoutFromName = this._mLayout.getLayoutFromName(
        this.computedLayout.layout_name
      );

      // message d'erreur pour indiquer que l'on a pas trouvé le layout
      if (!layoutFromName) {
        this.layoutFromName = {
          type: "message",
          class: "error",
          html: `Pas de layout trouvé pour le <i>layout_name</i> <b>${this.computedLayout.layout_name}</b>`,
        };
        return;
      }

      this.layoutFromName = layoutFromName;
    }

    if (this.computedLayout.overflow) {
      this.processHeightOverflow();
    }

    
    
    /** pour éviter de déclencher postComputeLayout s'il n'y a pas de changmeent effectif */
    if (!this.bPostComputeLayout) {
      return;
    }

    // comparaison entre le layout calculé et les données précédentes
    const dataCopy = utils.copy(this.data);
    const computedLayoutCopy = utils.copy(this.computedLayout);
    const dataChanged = !utils.fastDeepEqual(this.dataSave, dataCopy);
    const layoutChanged = !utils.fastDeepEqual(
      this.computedLayoutSave,
      computedLayoutCopy
    );

    if (
      this.computedLayoutSave &&
      this.dataSave &&
      !layoutChanged &&
      !dataChanged
    ) {
      return;
    }

    this.postComputeLayout(dataChanged, layoutChanged);

    // sauvegarde des données pour la prochaine comparaison
    this.dataSave = dataCopy;
    this.computedLayoutSave = computedLayoutCopy;
    
  }

  // pour gérer les composant avec overflow = true
  processHeightOverflow() {

    if (!(this.computedLayout?.overflow || this.layout?.overflow)) {
      return;
    }
    
    const elem = document.getElementById(this._id);
    if (!elem) {
      return;
    }
    
    const docHeight = document.body.clientHeight;

    // si la taille du body n'a pas changé on retourne
    if (this.docHeightSave == docHeight) {
      return;
    }

    // si on a reduit la fenetre
    // -> on remet à 0

    if (this.docHeightSave > docHeight || !this.docHeightSave) {
      this.computedLayout.style = {
        ...(this.computedLayout.style || {}),
        height: "200px",
        "overflow-y": "scroll",
      };

      this.layout.style = {
        ...(this.layout.style || {}),
        height: `200px`,
        "overflow-y": "scroll",
      };
    }

    this.docHeightSave = docHeight;

    setTimeout(() => {
      const parent = elem.closest("div.layout-item");
      const height = parent?.clientHeight;
      this.layout.style = {
        ...(this.layout.style || {}),
        height: `${height}px`,
        "overflow-y": "scroll",
      };
      
      this.computedLayout.style = {
        ...(this.computedLayout.style || {}),
        height: `${height}px`,
        "overflow-y": "scroll",
      };
    }, 200);
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
    utils.waitForElement(this._id).then(() => {
      this.processHeightAuto();
    });

    // on ajoute un évènement en cas de changement de la hauteur de la fenêtre
    window.addEventListener(
      "resize",
      (event) => {
        this.processHeightAuto();
      },
      true
    );
  }

  // action quand la taille change
  onHeightChange() {
    // this.processHeightAuto();
    this.processHeightOverflow();
  }

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
    const bodyHeight = `${document.body.clientHeight - elem.offsetTop}px`;

    // si la taille de l'élément correspond à la taille de la page
    // -> on ne fait rien

    if (elementHeight == bodyHeight && this.computedLayout.style.height == bodyHeight) {
      return;
    }

    this.computedLayout.style = this.computedLayout.style || {};
    this.computedLayout.style.height = bodyHeight;

    this.layout.style = this.layout.style || {};
    this.layout.style.height = bodyHeight;
    
    this._mLayout.reComputeHeight('auto');
  }

  // a redefinir pour faire des actions après processLayout
  postProcessLayout() {
  }

  // calcul de la marge pour l'afffichage du debug
  // - en fonction de l'input depth
  processDebug() {
    this.debugMarginLeft = `${10 * this.depth}px`;
  }

  emitAction(event) {
    this.onAction.emit(event);
  }

  /** pour les bouttons
   * quand layout.action est defini
   */
  onButtonClick(event) {
    const action = this.computedLayout.action;
    if (!action) {
      return;
    }

    // open modal TODO subject ?
    if (action.modal_name) {
      this._mLayout.openModal(action.modal_name, this.data);
      return;
    }

    if (action == "close") {
      this._mLayout.closeModals();
      return;
    }

    this.actionProcessing = true;
    this.onAction.emit({
      action: this.layout.action,
      data: this.data,
      layout: this.computedLayout,
    });
  }

  processAction(event) {
    if (event.type == "data-change") {
      this.computeLayout();
    }
    this.emitAction(event);
  }

  pretty(obj) {
    return JSON.stringify(obj, null, "____  ");
  }

  ngOnChanges(changes: SimpleChanges): void {
    for (const [key, change] of Object.entries(changes)) {
      if (
        utils.fastDeepEqual(change["currentValue"], change["previousValue"])
      ) {
        continue;
      }

      if (["layout", "data", "globalData"].includes(key)) {
        this.processLayout();
      }

      if (key == "debug") {
        this.processDebug();
      }
    }
  }

  onTabChanged($event) {
    this._mLayout.reDrawElem('tab changed')
  }
  
  refreshData(objectName) {
    
  }
}
