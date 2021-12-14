import { Injectable } from "@angular/core";

import { HttpClient } from "@angular/common/http";

import { Observable, Subject } from '@librairies/rxjs';
import { CommonService } from "@geonature_common/service/common.service";

@Injectable()
export class ModulesRequestService {

  // requêtes en cours
  private _pendingRequests = {};

  private _cacheRequests = {};

  constructor(
      private _http: HttpClient,
      private _commonService: CommonService,
  ) {}

  init() {
  }

  /**
   *
   */
  request(method, url, {params={}, data={}, useCache=false} = {}): Observable<any> {
    return new Observable<any>(observer => {
      const urlRequest = `${url}${this.sQueryParams(params)}`
      if ( useCache && this._cacheRequests[urlRequest]) {
        observer.next(this._cacheRequests[urlRequest]);
        return observer.complete();
        // return Observable.of(this._cacheRequests[urlRequest] as any);
      }

      let pendingSubject = method == 'get'
          ? this._pendingRequests[urlRequest]
          : null;

        if (!pendingSubject) {

          const pendingSubject = new Subject();
          this._pendingRequests[urlRequest] = pendingSubject;
          this._http[method](urlRequest, data)
            .subscribe(
              (value) => {
                if(useCache) {
                  this._cacheRequests[urlRequest] = value;
                }
                pendingSubject.next(value);
                pendingSubject.complete();
                observer.next(value);
                // delete this._pendingRequests[urlRequest];
                this._pendingRequests[urlRequest] = undefined;
                return observer.complete();
              },
              (error) => {
                var errorOut = error.error && error.error.description || error.error;
                var errorOutHTML = `method: ${method}<br> url: ${url}<br>error: ${errorOut}`
                errorOut = `method: ${method}, url: ${url}, error: ${errorOut}`
                pendingSubject.error(errorOut);
                this._pendingRequests[urlRequest] = undefined;
                this._commonService.regularToaster(
                  'error',
                  errorOutHTML,
                );
                return observer.error(errorOut);
              }
            );

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