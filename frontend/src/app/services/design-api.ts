import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { BuildRequest, BuildResponse, Catalog, DesignFailure, Manifest, PromptRequest } from '../models/design.models';

@Service()
export class DesignApi {
    private readonly http = inject(HttpClient);

    health() {
        return this.http.get<{ status: String; kernel: String }>('/health');
    }

    catalog() {
        return this.http.get<Catalog>('/catalog');
    }

    build(request: BuildRequest): Observable<BuildResponse> {
        return this.http.post<BuildResponse>('/designs', request).pipe(catchError(toFailure));
    }

    buildFromPrompt(request: PromptRequest): Observable<BuildResponse> {
        return this.http.post<BuildResponse>('/designs/from-prompt', request).pipe(catchError(toFailure))
    }

    manifest(designId: string) {
        return this.http.get<Manifest>(`/designs/${encodeURIComponent(designId)}/manifest`);
    }

    plateUrl(designId: string, plateNumber: number): string {
        return `/designs/${encodeURIComponent(designId)}/plates/${plateNumber}`;
    }
    
}

function toFailure(err: HttpErrorResponse): Observable<never> {
        const body = err.error ?? {};
        let failure: DesignFailure;
        if (err.status === 422 && Array.isArray(body.issues)) {
            failure = { kind: 'issues', issues: body.issues };
        } else if (err.status === 422 && Array.isArray(body.detail)) {
            failure = { kind: 'message', message: body.detail.map((d: any) =>
                 `${d.loc?.join('.')}: ${d.msg}`
            ).join('\n') };
        } else if (err.status === 409) {
            failure = { kind: 'questions', questions: body.questions ?? [], spec: body.spec };
        } else if (err.status === 0) {
            failure = {kind: 'message', message: 'Backend not reachable. Is uvicorn running on port 8000?' };
        } else {
            failure = { kind: 'message', message: body.detail ?? err.message };
        }
        return throwError(() => failure);
    }
