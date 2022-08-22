import { Component, OnInit, Injector, Inject } from "@angular/core";
import { ModulesLayoutComponent } from "./layout.component";
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from "@angular/material/dialog";

import utils from "../../../utils";

export interface DialogData {
  data: any;
  layout: any;
  debug: any;
}

@Component({
  selector: "modules-layout-modal",
  templateUrl: "layout-modal.component.html",
  styleUrls: ["../../base/base.scss", "layout-modal.component.scss"],
})
export class ModulesLayoutModalComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  isOpen = false;
  // _matDialog: MatDialog;
  processedLayout;

  modalOpenSubscription;
  modalCloseSubscription;

  constructor(_injector: Injector) {
    super(_injector);
    this._name = "layout-modal";
    // this._matDialog = this._injector.get(MatDialog);
    this.bPostComputeLayout = true;
  }

  // postInit(): void {
  //   this.initModal();
  // }

  // processLayout(): void {
  //   this.initModal();
  // }

  postComputeLayout(dataChanged, layoutChanged): void {
    this.initModal();
  }

  initModal() {
    if (!this.modalOpenSubscription) {
      this._mLayout.initModal(this.computedLayout.modal_name);
      this.modalOpenSubscription = this._mLayout.modals[
        this.computedLayout.modal_name
      ].subscribe((data) => {
        this.data = data;
        this.openDialog();
      });
      this.modalCloseSubscription = this._mLayout.$closeModals.subscribe(() => {
        this.closeDialog();
      });
    }
  }

  closeDialog() {
    this.isOpen = false;
  }

  openDialog() {
    this.processedLayout = utils.copy(this.layout);
    delete this.processedLayout.type;
    this.isOpen = true;
    setTimeout(() => {
      const modalContainer = document.querySelector("div.modal-container");

      modalContainer?.addEventListener("click", (event) => {
        this.closeDialog();
      });

      const modalContent = document.querySelector(
        "div.modal-content"
      ) as HTMLElement;

      modalContent.focus();
      modalContent?.addEventListener("click", (event) => {
        event.stopPropagation();
      });
    });
  }
}
