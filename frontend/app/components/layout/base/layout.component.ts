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
  @Input() direction: "string";

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

  constructor(protected _injector: Injector) {
    this._name = "layout";
    this._id = Math.round(Math.random() * 1e10);
    this._mLayout = _injector.get(ModulesLayoutService);
  }

  ngOnInit() {
    // initialisation du layout
    this.processLayout();

    // subscription pour recalculer le layout
    this._mLayout.$reComputeLayout.pipe().subscribe(() => {
      this.computeLayout();
    });

    this._mLayout.$recomputedHeight.pipe().subscribe(() => {
      this.onHeightChange();
    });

    // pour les élément avec heigh_auto = true
    this.listenPageResize();

    // lorque une postInitialisation est nécessaire
    this.postInit();
  }

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
      elemId: this._id,
    });

    // récupération des données associées à this.computedLayout.key
    this.dataKey =
      this.layoutType == "key" &&
      utils.getAttr(this.data, this.computedLayout.key);

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

    // this.processHeightOverflow();

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
    if (!this.computedLayout?.overflow) {
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
        height: "100px",
        "overflow-y": "scroll",
      };

      this.layout.style = {
        ...(this.layout.style || {}),
        height: `100px`,
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
    }, 50);
  }

  listenPageResize() {
    if (!this.computedLayout?.height_auto) {
      return;
    }

    utils.waitForElement(this._id).then(() => this.processHeightAuto());
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
    this.processHeightOverflow();
    this.processHeightAuto();
  }

  /** pour mettre les layout avec height_auto = true à la hauteur totale de la page */
  processHeightAuto() {
    const elem = document.getElementById(this._id);

    if (!elem) {
      return;
    }

    if(!this.computedLayout.height_auto){
      return;
    }

    const elementHeight = elem && `${elem.clientHeight}px`;
    const bodyHeight = `${document.body.clientHeight - elem.offsetTop}px`;

    // si la taille de l'élément correspond à la taille de la page
    // -> on ne fait rien
    if (elementHeight == bodyHeight) {
      return;
    }

    this.computedLayout.style = this.computedLayout.style || {};
    this.computedLayout.style.height = bodyHeight;
    setTimeout(() => {
      this._mLayout.reComputeHeight(this._name);
    }, 10);
  }

  // a redefinir pour faire des actions après processLayout
  postProcessLayout() {}

  // calcul de la margr
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
    }

    this.onAction.emit({
      action: this.layout.action,
      data: this.data,
      layout: this.layout,
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
      this._mLayout.reComputeHeight('truc');
  }
}
