import { Component, signal } from '@angular/core';
import { SideNav } from './components/side-nav/side-nav';

@Component({
  imports: [SideNav],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('frontend');
}
