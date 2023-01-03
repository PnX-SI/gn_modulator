import { Injectable, Injector } from '@angular/core';
import { ModulesConfigService } from './config.service';
@Injectable()
export class ModulesSchemaService {
  _mConfig: ModulesConfigService;

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
  }

  property(schemaCode, key) {
    const schema = this._mConfig.schema(schemaCode);
    if (key.includes('.')) {
      let keys = key.split('.');
      let keyRel = keys.shift();
      let keyProp = keys.join('.');
      let propertyRel = this.property(schemaCode, keyRel);
      return {
        ...this.property(propertyRel.schema_code, keyProp),
        parent: propertyRel,
      };
    }
    return {
      key,
      ...schema.properties[key],
    };
  }
}
