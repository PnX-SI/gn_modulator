import { ModulesConfigService } from './config.service';
import { ModulesRouteService } from './route.service';
import { ModulesDataService } from './data.service';
import { ModulesLayoutService } from './layout.service';
import { ModulesFormService } from './form.service';
import { ModulesRequestService } from './request.service';
import { ModulesMapService } from './map.service';
import { ModulesTableService } from './table.service';
import { ModulesObjectService } from './object.service';
import { ModulesPageService } from './page.service';
import { ListFormService } from './list-form.service';

export default [
  ModulesConfigService,
  ModulesDataService,
  ModulesLayoutService,
  ModulesFormService,
  ModulesRequestService,
  ListFormService,
  ModulesMapService,
  ModulesRouteService,
  ModulesTableService,
  ModulesPageService,
  ModulesObjectService,
];
