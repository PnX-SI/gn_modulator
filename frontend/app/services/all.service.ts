import { Injectable } from '@angular/core';

import { AuthService } from '@geonature/components/auth/auth.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ActivatedRoute, Router } from '@angular/router';

import { ModulesConfigService } from './config.service';
import { ModulesRequestService } from './request.service';
import { ModulesDataService } from './data.service';
import { ModulesFormService } from './form.service';
import { ModulesLayoutService } from './layout.service';
import { ModulesMapService } from './map.service';
import { ModulesRouteService } from './route.service';
import { ModulesSchemaService } from './schema.service';

@Injectable()
export class ModulesService {
  constructor(
    public auth: AuthService,
    public commonService: CommonService,
    public mapService: ModulesMapService,
    public mConfig: ModulesConfigService,
    public mData: ModulesDataService,
    public mLayout: ModulesLayoutService,
    public mForm: ModulesFormService,
    public mRoute: ModulesRouteService,
    public route: ActivatedRoute,
    public router: Router,
    public request: ModulesRequestService,
    public schema: ModulesSchemaService
  ) {}
}
