import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { Observable, Subject } from '@librairies/rxjs';
import { CommonService } from '@geonature_common/service/common.service';
import utils from '../utils';

@Injectable()
export class ModulesRequestService {
  // requêtes en cours
  private _pendingRequests = {};

  private _cacheRequests = {};

  constructor(private _http: HttpClient, private _commonService: CommonService) {}

  init() {}

  /** Renvoie l'url en prenant en compte les query params */
  url(baseUrl, params = {}) {
    return `${baseUrl}${this.sQueryParams(params)}`;
  }

  dataHasFile(data) {
    return Object.values(data).some((v) => utils.isFile(v));
  }

  httpRequestWithFormData(url, data) {
    const formData = new FormData();
    for (const [key, value] of Object.entries(data).filter(
      ([key, value]) => !utils.isFile(value)
    )) {
      formData.append(key, value as any);
    }
    for (const [key, value] of Object.entries(data).filter(([key, value]) => utils.isFile(value))) {
      formData.append(key, value as any);
    }
    const params = new HttpParams();
    return this._http.request(
      new HttpRequest('POST', url, formData, {
        params: params,
        reportProgress: true,
        responseType: 'json',
      })
    );
  }

  postRequestWithFormData(url, { params = {}, data = {} }) {
    const urlRequest = this.url(url, params);
    return this.httpRequestWithFormData(urlRequest, data);
  }

  /** */
  request(method, url, { params = {}, data = {}, cache = false } = {}): Observable<any> {
    return new Observable<any>((observer) => {
      const urlRequest = this.url(url, params);

      if (cache && this._cacheRequests[urlRequest]) {
        observer.next(this._cacheRequests[urlRequest]);
        return observer.complete();
      }

      // mise en cache et pendingSubject seulement pour les get
      let pendingSubject = method == 'get' ? this._pendingRequests[urlRequest] : null;

      if (!pendingSubject) {
        const pendingSubject = new Subject();
        this._pendingRequests[urlRequest] = pendingSubject;

        this._http[method](urlRequest, data).subscribe(
          (value) => {
            if (cache) {
              this._cacheRequests[urlRequest] = value;
            }
            pendingSubject.next(value);
            pendingSubject.complete();
            observer.next(value);
            // delete this._pendingRequests[urlRequest];
            this._pendingRequests[urlRequest] = undefined;
            return observer.complete();
          },
          (error: HttpErrorResponse) => {
            var errorOut = (error.error && error.error.description) || error.error;
            var errorOutHTML = `method: ${method}<br> url: ${url}<br>error: ${errorOut}`;
            errorOut = `method: ${method}, url: ${url}, error: ${errorOut}`;
            pendingSubject.error(errorOut);
            this._pendingRequests[urlRequest] = undefined;
            this._commonService.regularToaster('error', errorOutHTML);
            return observer.error(errorOut);
          }
        );
      } else {
        pendingSubject.asObservable().subscribe((value) => {
          observer.next(value);
          return observer.complete();
        });
      }
    });
  }

  sQueryParams(params) {
    if (!params) {
      return '';
    }
    let queryParams = Object.entries(params)
      .filter(([k, v]) => ![null, undefined, ''].includes(v as any))
      .map(([k, v]) => {
        let sParam;
        if (Object(v) === v) {
          sParam = JSON.stringify(v);
        } else if (!!v) {
          sParam = v;
        }
        return `${k}=${sParam}`;
      });

    return queryParams.length ? `?${queryParams.join('&')}` : '';
  }
}
