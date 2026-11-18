export type Matrix16 = number[];
// What i send
export interface HardwareUse { id: string; ref: string; }
export interface PartSpec { id: string; template: string; params: Record<string, unknown>; }
export interface Connection {
    a: string;
    b: string;
    kind: 'fixed' | 'revolute';
    interface?: string | null;
    range_deg?: [number, number] | null;
    rest_deg?: number;
}
export interface DesignSpec {
    intent: string;
    hardware: HardwareUse[];
    parts: PartSpec[];
    connections: Connection[];
    assumptions?: string[];
    questions?: string[];
}
export interface BuildRequest { spec: DesignSpec; printer?: string; material?: string; }
export interface PromptRequest { prompt: string; printer?: string; material?: string; ask_user?: boolean; }


// What you get back
export interface Issue {
    code: string;
    severity: 'error' | 'warning';
    message: string;
    part?: string | null;
    site?: string | null;
    hint?: string | null;
    data?: Record<string, unknown>;
}
export interface Joint {
    kind: 'fixed' | 'revolute';
    interface: string | null;
    min: number;
    max: number;
    value: number;                   
    parent_frame: Matrix16;
    child_offset: Matrix16;
}
export interface ManifestPart {
    id: string;
    template: string;
    parent: string | null;
    world: Matrix16;                 
    bodies: { name: string; mesh: string }[];
    holds: { hardware: string; ref: string | null; pose: Matrix16 }[];
    joint?: Joint;
}
export interface Manifest {
    id: string;
    units: 'mm';
    up: 'Z';
    matrix_order: 'row-major';
    root: string;
    parts: ManifestPart[];
    issues: Issue[];
}
export interface PlateItem { key: string; matrix: Matrix16; }
export interface PlatePlan {
    printer: string;
    bed: { shape: 'rect' | 'circle'; width: number; depth: number; margin: number };
    usable: [number, number, number, number];
    max_height: number;
    plates: PlateItem[][];
}
export interface BuildResponse {
    design_id: string;
    manifest: Manifest;
    plates: PlatePlan;
    files: string[];
    warnings: Issue[];
}
export interface CatalogTemplate {
    name: string;
    description: string;
    sites: Record<string, string[]>;
    hardware_categories: string[];
    params: Record<string, unknown>;  
}
export interface Catalog {
    hardware: string[];
    interfaces: string[];
    printers: string[];
    materials: string[];
    templates: CatalogTemplate[];
}


export type DesignFailure =
    | { kind: 'issues'; issues: Issue[] }                         
    | { kind: 'questions'; questions: string[]; spec: DesignSpec } 
    | { kind: 'message'; message: string };                       
