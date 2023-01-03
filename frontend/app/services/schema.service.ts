import { Injectable, Injector } from '@angular/core';
import { ModulesConfigService } from './config.service';
import utils from '../utils';

@Injectable()
export class ModulesSchemaService {
  _mConfig: ModulesConfigService;

  constructor(private _injector: Injector) {
    this._mConfig = this._injector.get(ModulesConfigService);
  }

  property(schemaCode, key) {
    const schema = utils.copy(this._mConfig.schema(schemaCode));
    if (key.includes('.')) {
      let keys = key.split('.');
      let keyRel = keys.shift();
      let keyProp = keys.join('.');
      let propertyRel = this.property(schemaCode, keyRel);
      let propertyProp = this.property(propertyRel.schema_code, keyProp);
      if (propertyProp.parent) {
        propertyProp.parent.parent = propertyRel;
      } else {
        propertyProp.parent = propertyRel;
      }

      propertyProp.key = key;

      return propertyProp;
    }

    return {
      key,
      ...schema.properties[key],
    };
  }
}
