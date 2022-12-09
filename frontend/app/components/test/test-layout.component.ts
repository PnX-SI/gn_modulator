import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ModulesContextService } from '../../services/context.service';
import { ModulesConfigService } from '../../services/config.service';
import utils from '../../utils';
@Component({
  selector: 'modules-test-layout',
  templateUrl: 'test-layout.component.html',
  styleUrls: ['../base/base.scss', 'test-layout.component.scss'],
})
export class TestLayoutComponent implements OnInit {
  /**  du formulaire du layout */

  testLayoutForm;

  test = {
    layout: {
      title: 'Test Layout',
    },
    data: {},
  };

  rawLayout: any = {
    layout: JSON.stringify(this.test, null, 4),
  };

  debug;
  error: null;

  layout: any;

  layoutCode: string;
  value;

  data: any = {
    display_form: false,
  };

  constructor(
    private _route: ActivatedRoute,
    private _mContext: ModulesContextService,
    private _mConfig: ModulesConfigService
  ) {}

  ngOnInit() {
    this._mConfig.init().subscribe(() => {
      this._route.queryParams.subscribe((params) => {
        this.debug = ![undefined, false, 'false'].includes(params.debug);
        this.layoutCode = params.layout_code;
        this.value = params.value;
        this.initLayout();
      });
      this.initLayout();
    });
  }

  initLayout() {
    this.rawLayout.layout_from_list = null;
    this.rawLayout.debug = null;
    this.layout = null;
    this.data = null;
    this.testLayoutForm = {
      title: 'Définition',
      appearance: 'outline',
      type: 'form',
      change: `__f__(event) => {
           if('layout_from_list' in event) {
             context.form_group.patchValue({
               layout_definition: ''
             });
            context.form_group.patchValue({
               layout_definition: x.utils.YML.dump(event.layout_from_list)
             });
           }
          }
        `,
      items: [
        {
          direction: 'row',
          flex: '0',
          items: [
            {
              flex: '0',
              type: 'button',
              icon: 'refresh',
              description: 'Recharger le layout',
              click: `__f__(event) => {
              context.form_group.patchValue({
                oups: !context.form_group.value.oups,
                layout_definition: '',
                layout_from_list: { code: data.layout_from_list.code },
              });
              }`,
            },
            {
              flex: '0',
              type: 'boolean',
              key: 'debug',
              default: this.debug
            },
          ],
        },
        {
          hidden: true,
          type: 'boolean',
          key: 'oups',
        },
        {
          flex: '0',
          key: 'layout_from_list',
          title: `Selection de layout`,
          type: 'list_form',
          api: '/modules/layouts/',
          value_field_name: 'code',
          label_field_name: 'title',
          title_field_name: 'description',
          return_object: true,
          oup: '__f__data.oups',
          // reload_on_search: true,
          default_item: this.layoutCode && { code: this.layoutCode },
        },
        {
          flex: '0',
          key: 'layout_definition',
          type: 'textarea',
          title: 'Layout',
          display: 'form',
          min_rows: '5',
          max_rows: '30',
          style: {
            'overflow-y': 'scroll',
          },
        },
      ],
    };
    this.process();
  }

  process() {
    let layoutDefinitionJson = utils.parseYML(this.rawLayout.layout_definition);
    this.layout = null;
    this.data = null;
    if (!layoutDefinitionJson || layoutDefinitionJson == 'undefined') {
      return;
    }
    setTimeout(() => {
      this._mContext.initContext(layoutDefinitionJson.context || {});
      this.layout = layoutDefinitionJson.layout;
      this.data = layoutDefinitionJson.data || {};
    });
  }

  processAction(event) {
    if (event.type == 'data-change') {
      this.process();
    }
  }
}
