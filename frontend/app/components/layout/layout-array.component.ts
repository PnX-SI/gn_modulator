import { Component, OnInit } from "@angular/core";
import { ModulesFormService } from "../../services/form.service";
import { ModulesLayoutService } from "../../services/layout.service";
import utils from "../../utils";

import { ModulesLayoutComponent } from "./layout.component";
@Component({
  selector: "modules-layout-array",
  templateUrl: "layout-array.component.html",
  styleUrls: ["../base/base.scss", "layout-array.component.scss"],
})
export class ModulesLayoutArrayComponent
  extends ModulesLayoutComponent
  implements OnInit
{
  /** options pour les elements du array */

  // arrayOptions: Array<any>;

  constructor(
    private _formService: ModulesFormService,
    _mLayout: ModulesLayoutService
  ) {
    super(_mLayout);
    this._name = "layout-array";
  }

  postComputeLayout(): void {
    const layoutIndex =
      this.layout &&
      this.layout.findIndex &&
      this.layout.findIndex((l) => l["overflow"]);
    if ([-1, null, undefined].includes(layoutIndex)) {
      return;
    }

    console.log("postprocess array");
    setTimeout(() => {
      if (!document.getElementById(`${this._id}.0`)) {
        return;
      }
      const heightParent = document
        .getElementById(`${this._id}.0`)
        .closest(".layout-section").clientHeight;

      const heightSibblings = this.layout
        .map(
          (l, ind) => document.getElementById(`${this._id}.${ind}`).clientHeight
        )
        .filter((l, ind) => ind != layoutIndex)
        .reduce((acc, cur) => acc + cur);

      console.log(heightParent, heightSibblings);
      const height = heightParent - heightSibblings;
      // const height = 300;

      this.layout[layoutIndex].style = {
        ...(this.computedLayout[layoutIndex].style || {}),
        "overflow-y": "scroll",
        height: `${height}px`,
      };

      /** pour redéclencher le calcul des layout */
      // this._mLayout.reComputeLayout();
    }, 400);
  }

  arrayOptions(index) {
    return {
      ...this.options,
      index,
      formGroup:
        this.options.formGroup &&
        this.options.formGroup.get(this.layout.key).at(index),
    };
  }

  processAction(action) {
    if (action.type == "remove-array-element") {
      this.data[this.layout.key].splice(action.index, 1);
      this._formService.setControl(
        this.options.formGroup,
        this.layout,
        this.data,
        this.globalData
      );
    } else {
      this.emitAction(action);
    }
  }

  addArrayElement() {
    this.data[this.layout.key].push({});
    this._formService.setControl(
      this.options.formGroup,
      this.layout,
      this.data,
      this.globalData
    );
  }
}
