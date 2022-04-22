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

  testLayoutForm = {
    title: "Définition",
    appearance: "outline",
    type: "form",
    items: [
      // {
      //   key: "layout_from_list",
      //   title: "Selection de layout",
      //   type: "list_form",
      //   api: "/modules/layouts/",
      //   label_field_name: "layout_name",
      //   title_field_name: "layout_description",
      //   return_object: true,
      //   data_reload_on_search: true,
      //   default: { layout_name: "test_list" },
      //   change: [
      //     "__f__{",
      //     "  setTimeout(()=> {",
      //     "    formGroup.patchValue({layout:JSON.stringify(data.layout_from_list, null, 4)});",
      //     "  }, 10);",
      //     "}",
      //   ],
      // },
      {
        key: "layout",
        type: "textarea",
        title: "Layout",
        display: "form",
        min_rows: "5",
        max_rows: "30",
      },
    ],
  };

  test = {
    layout: {
      type: "form",
      appearance: "fill",
      items: [
        {
          key: "minmax",
          type: "integer",
          min: 0,
          max: 10,
          required: true,
        },
        {
          direction: "row",
          items: [
            {
              type: "message",
              // hidden: "__f__!formGroup.errors",
              json: "__f__utils.getFormErrors(formGroup)",
            },
            {
              type: "message",
              // hidden: "__f__!formGroup.errors",
              json: "__f__formGroup.value",
            },
          ],
        },
      ],
    },
    data: {},
  };

  rawLayout: any = {
    layout: JSON.stringify(this.test, null, 4),
  };

  error: null;

  layout: any;

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
    });
    this.process();
  }

  getTestLayoutForm;

  process() {
    this.layout = null;
    this.data = null;
    let json = utils.parseJSON(this.rawLayout.layout);
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
