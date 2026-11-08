import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StudioLayout } from './studio-layout';

describe('StudioLayout', () => {
  let component: StudioLayout;
  let fixture: ComponentFixture<StudioLayout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StudioLayout],
    }).compileComponents();

    fixture = TestBed.createComponent(StudioLayout);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
