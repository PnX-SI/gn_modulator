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
    const schema = this._mConfig.schema(schemaCode);
    if (!schema) {
      return {};
    }

    if (key.includes('.')) {
      let keys = key.split('.').filter((k) => !Number.isInteger(Number.parseInt(k)));
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
      ...utils.copy(schema.properties[key]),
      required: schema?.properties[key]?.required || (schema.required || []).includes(key),
    };
  }
}
