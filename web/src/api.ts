export type Measure = "indice" | "mensual" | "anual";
export type Status = "disponible" | "sin_publicacion" | "sin_datos" | "sin_denominador" | "sin_valor_fuente" | "no_publicado";

export interface Meta {
  estado: Status;
  version_datos: string | null;
  ultima_carga_exitosa: string | null;
  periodo_fuente_max?: string;
  fuente: string;
  fuente_url: string;
}

export interface Metric { valor: number | null; estado: Status; unidad: string }
export interface Summary { periodo: string | null; indice: Metric; mensual: Metric; anual: Metric }
export interface HistoryPoint { periodo: string; valor: number | null; estado: Status }
export interface Envelope<T> { datos: T; meta: Meta }

const base = "/api/inflacion/v1";

async function request<T>(path: string, signal?: AbortSignal): Promise<Envelope<T>> {
  const response = await fetch(`${base}${path}`, { signal });
  if (!response.ok) throw new Error(response.status === 503 ? "La API no está lista." : "No se pudo consultar la API.");
  return response.json() as Promise<Envelope<T>>;
}

export function getSummary(period?: string, signal?: AbortSignal) {
  const query = period ? `?geografia=mx&periodo=${period}` : "?geografia=mx";
  return request<Summary>(`/resumen${query}`, signal);
}

export function getHistory(measure: Measure, from: string, until: string, signal?: AbortSignal) {
  const params = new URLSearchParams({ geografia: "mx", rubro: "general", medida: measure, desde: from, hasta: until });
  return request<HistoryPoint[]>(`/series?${params}`, signal);
}
