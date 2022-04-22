import {
  Component,
  OnInit,
  Input,
  SimpleChanges,
  EventEmitter,
  Output,
} from "@angular/core";
import { ModulesLayoutService } from "../../services/layout.service";
import utils from "../../utils";

@Component({
  selector: "modules-layout",
  templateUrl: "layout.component.html",
  styleUrls: ["../base/base.scss", "layout.component.scss"],
})
export class ModulesLayoutComponent implements OnInit {
  /** agencement */

  @Input() layout: any;
  @Input() computedLayout: any;
  // @Output() layoutChange = new EventEmitter<any>();

  // @Input() layoutDefinition: any;

  /** données */
  @Input() data: any;
  @Input() globalData: any;

  /** actions */
  @Output() onAction = new EventEmitter<any>();

  /** debug */
  @Input() debug: any;

  /** debug */
  @Input() depth = 0;

  @Input() direction: "string";

  @Input() options: any = {};

  /** margin for debug display
   * help with debugging nested layout
   */
  debugMarginLeft = "0px";

  /** Type de layout
   * items: liste de layout
   */
  layoutType: string;

  prettyDebug;

  dataKey;

  _name: string;
  _id;

  isInitialized = false;

  constructor(protected _mLayout: ModulesLayoutService) {
    this._name = "layout";
    this._id = Math.round(Math.random() * 1e10);
  }

  ngOnInit() {
    this.processLayout();
    this._mLayout.$reComputeLayout.subscribe(() => {
      this.computeLayout();
    });
    this.listenResize();
  }

  log(...args) {
    console.log(this._name, this.layout && this.layout.type, this._id, ...args);
  }

  debugLog(...args) {
    this.debug && this.log(...args);
  }

  getFormGroup() {
    return this.options.formGroup;
  }

  postComputeLayout() {};

  computeLayout() {
    this.layoutType =
      this.layoutType || this._mLayout.getLayoutType(this.layout);

    this.computedLayout = this._mLayout.computeLayout({
      layout: this.layout,
      data: this.data,
      globalData: this.globalData,
      formGroup: this.getFormGroup(),
      elemId: this._id
    });
    this.dataKey =
      this.layoutType == "key" && utils.getAttr(this.data, this.layout.key);
    this.prettyDebug = {
      layout: this.pretty(this.computedLayout),
      data: this.pretty(this.data),
      dataKey: this.pretty(this.dataKey),
    };
    this.postComputeLayout();
  }

  processLayout() {
    this.globalData = this.globalData || this.data;
    this.computeLayout();
    this.postProcessLayout();
    this.listenResize();
    this.isInitialized = true;
  }

  listenResize() {
    if(!this.computedLayout.height_auto) {
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

  processHeightAuto() {
    if (
      !(
        this.computedLayout &&
        this.computedLayout.height_auto &&
        document.getElementById(this._id)
      )
    ) {
      return;
    }
    const elem = document.getElementById(this._id);
    const height = document.body.clientHeight - elem.offsetTop;
    this.layout.style = this.computedLayout.style || {};
    this.layout.style.height = `${height}px`;
    this._mLayout.reComputeLayout();
  }

  postProcessLayout() {}

  processDebug() {
    this.debugMarginLeft = `${10 * this.depth}px`;
  }

  emitAction(event) {
    this.onAction.emit(event);
  }

  emitLayoutAction() {
    if (!this.layout.action) {
      return;
    }
    this.onAction.emit({
      action: this.layout.action,
      data: this.data,
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
}
