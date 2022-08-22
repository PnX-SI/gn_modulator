import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { ModulesLayoutService } from "../../services/layout.service";
import utils from "../../utils";
@Component({
  selector: "modules-test-layout",
  templateUrl: "test-layout.component.html",
  styleUrls: ["../base/base.scss", "test-layout.component.scss"],
})
export class TestLayoutComponent implements OnInit {
  /**  du formulaire du layout */

  testLayoutForm;

  test = {
    layout: {
      title: "Test Layout",
    },
    data: {},
  };

  rawLayout: any = {
    layout: JSON.stringify(this.test, null, 4),
  };

  error: null;

  layout: any;

  layoutName: string;
  value;

  data: any = {
    display_form: false,
  };

  debug;

  constructor(
    private _route: ActivatedRoute,
    private _mLayout: ModulesLayoutService
  ) {}

  ngOnInit() {
    this._route.queryParams.subscribe((params) => {
      this.debug = ![undefined, false, "false"].includes(params.debug);
      this.layoutName = params.layout_name;
      this.value = params.value
      this.initLayout();
    });
    this.initLayout();
  }

  initLayout() {
    this.rawLayout.layout_from_list = null;
    this.layout = null;
    this.data = null;
    setTimeout(() => {
      this.testLayoutForm = {
        title: "Définition",
        appearance: "outline",
        type: "form",
        change: [
          "__f__(event) => {",
          " if('layout_from_list' in event) {",
          "   formGroup.patchValue({",
          "     layout: ''",
          "   });",
          "   formGroup.patchValue({",
          "     layout: JSON.stringify(event.layout_from_list, 4, '    ')",
          "   });",
          " }",
          "}",
        ],
        items: [
          {
            flex: '0',
            key: "layout_from_list",
            title: `Selection de layout`,
            type: "list_form",
            api: "/modules/layouts/",
            value_field_name: "layout_name",
            label_field_name: "layout_name",
            title_field_name: "layout_description",
            return_object: true,
            data_reload_on_search: true,
            default: this.layoutName && { layout_name: this.layoutName },
          },
          {
            flex: '0',
            key: "layout",
            type: "textarea",
            title: "Layout",
            display: "form",
            min_rows: "5",
            max_rows: "30",
          },
        ],
      };
    });
  }

  process() {
    let json = utils.parseJSON(this.rawLayout.layout);
      this.layout = null;
      this.data = null;
      setTimeout(() => {
        this.layout = json && json.layout;
        this.data = json && json.data;
      });

  }

  processAction(event) {
    if (event.type == "data-change") {
      this.process();
    }
  }
}
