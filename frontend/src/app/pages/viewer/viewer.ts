import { Component, DestroyRef, ElementRef, afterNextRender, inject, signal, viewChild } from '@angular/core';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DesignApi } from '../../services/design-api';
import { DesignFailure, DesignSpec, Manifest } from '../../models/design.models';

const SPEC: DesignSpec = {
  intent: 'Raspberry Pi 4 case with a camera on a turning arm',
  hardware: [
    { id: 'pi', ref: 'raspberry_pi_4b' },
    { id: 'cam', ref: 'rpi_camera_module_3' },
  ],
  parts: [
    { id: 'case', template: 'enclosure', params: { hardware: 'pi' } },
    { id: 'arm', template: 'link', params: { length: 'auto' } },
    { id: 'camera_mount', template: 'sensor_mount', params: { hardware: 'cam' } },
  ],
  connections: [
    { a: 'case.top', b: 'arm.base', kind: 'revolute', interface: 'revolute_pin', range_deg: [-90, 90] },
    { a: 'arm.tip', b: 'camera_mount.base', kind: 'fixed', interface: 'screw_m2_5' },
  ],
};

const COLOURS = [0x8fa8c8, 0xc8a08f, 0x9fc88f, 0xc8c08f, 0xb08fc8];

@Component({
  imports: [],
  selector: 'app-viewer',
  styleUrl: './viewer.scss',
  templateUrl: './viewer.html',
})
export class Viewer {
  private readonly api = inject(DesignApi);
  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef)
  private readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  readonly status = signal('Building the design please wait...');

  private renderer?: THREE.WebGLRenderer;
  private controls?: OrbitControls;
  private resizeObserver?: ResizeObserver;
  private readonly scene = new THREE.Scene();
  private readonly camera = new THREE.PerspectiveCamera(45, 1, 1, 20000);

  constructor() {
    afterNextRender(() => {
      this.setupScene();
      this.buildDesign();
    });

    inject(DestroyRef).onDestroy(() => {
      this.renderer?.setAnimationLoop(null);
      this.resizeObserver?.disconnect();
      this.controls?.dispose();
      this.renderer?.dispose();
    });
  }

  private setupScene(): void {
    const canvas = this.canvas().nativeElement;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    this.camera.up.set(0, 0, 1);                                
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 1.6));

    const sun = new THREE.DirectionalLight(0xffffff, 1.8);
    sun.position.set(300, -400, 600);
    this.scene.add(sun);

    const grid = new THREE.GridHelper(400, 40, 0x888888, 0xcccccc);
    grid.rotation.x = Math.PI / 2;                              
    this.scene.add(grid);

    this.controls = new OrbitControls(this.camera, canvas);
    this.camera.position.set(250, -300, 220);

    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(this.host.nativeElement);
    this.resize();

    this.renderer.setAnimationLoop(() => this.renderer!.render(this.scene, this.camera));
  }

  private resize(): void {
    const { clientWidth: w, clientHeight: h } = this.host.nativeElement;
    if (!this.renderer || w === 0 || h === 0) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  private buildDesign(): void {
    this.api.build({ spec: SPEC }).subscribe({
      next: result => void this.showDesign(result.manifest),
      error: (f: DesignFailure) => this.status.set(
        f.kind === 'message' ? f.message
          : f.kind === 'issues' ? f.issues.map(i => i.message).join(' · ')
            : 'The AI has questions'),
    });
  }

  private async showDesign(manifest: Manifest): Promise<void> {
    const loader = new GLTFLoader();
    const bounds = new THREE.Box3();

    for (const [i, part] of manifest.parts.entries()) {
      const group = new THREE.Group();
      group.matrixAutoUpdate = false;
      group.matrix.fromArray(part.world).transpose();         

      const material = new THREE.MeshStandardMaterial({
        color: COLOURS[i % COLOURS.length],
        roughness: 0.75,
      });

      for (const body of part.bodies) {
        const gltf = await loader.loadAsync(body.mesh);         
        gltf.scene.traverse(obj => {
          if (obj instanceof THREE.Mesh) {
            if (!obj.geometry.getAttribute('normal')) obj.geometry.computeVertexNormals();
            obj.material = material;
          }
        });
        group.add(gltf.scene);
      }

      this.scene.add(group);
      group.updateMatrixWorld(true);
      bounds.expandByObject(group);
    }

    this.frameCamera(bounds);
    this.status.set(`Design ${manifest.id}: ${manifest.parts.length} parts`);
  }

  private frameCamera(bounds: THREE.Box3): void {
    if (bounds.isEmpty() || !this.controls) return;
    const centre = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3()).length();
    this.controls.target.copy(centre);
    this.camera.position.copy(centre).add(new THREE.Vector3(0.9, -1.1, 0.8).multiplyScalar(size));
    this.controls.update();
  }
}
