import { Injectable } from "@angular/core";

import { HttpClient } from "@angular/common/http";

import { Observable, Subject } from '@librairies/rxjs';

@Injectable()
export class ModulesRequestService {

  // requêtes en cours
  pendingRequests = {};

  constructor(
      private _http: HttpClient
  ) {}

  init() {
  }

  /**
   *
   */
  request(method, url, {params={}, data={}} = {}) {

    return new Observable(observer => {
      const url_request = `${url}${this.sQueryParams(params)}`
        let pendingSubject = method == 'get'
          ? this.pendingRequests[url_request]
          : null;

        if (!pendingSubject) {
          const pendingSubject = new Subject();
          this.pendingRequests[url_request] = pendingSubject;
        this._http[method](url_request, data)
          .subscribe((value) => {
            pendingSubject.next(value);
            pendingSubject.complete();
            observer.next(value);
            // delete this.pendingRequests[url_request];
            this.pendingRequests[url_request] = undefined;
        return observer.complete();
          });
        } else {
          pendingSubject
          .asObservable()
          .subscribe((value) => {
            observer.next(value);
            return observer.complete();
          });
        }
    });

  }


  sQueryParams(params) {
    if(!params){
        return '';
    }
    let queryParams = Object.entries(params)
      .filter(([k, v]) => ![null, undefined].includes(v))
      .map(([k, v])=> {
        let sParam;
        if(Object(v) === v) {
            sParam = JSON.stringify(v);
        } else if (!!v) {
            sParam = v;
        }
        return `${k}=${sParam}`;
    });

    return queryParams.length
        ? `?${queryParams.join('&')}`
        : ''
    ;
  }

}