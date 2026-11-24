import { TestBed } from '@angular/core/testing';
import { DesignApi } from './design-api';

describe('DesignApi', () => {
  let service: DesignApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DesignApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
