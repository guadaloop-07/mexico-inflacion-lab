import { useEffect, useMemo, useRef, useState } from "react";
import { getHistory, getSummary, type HistoryPoint, type Measure, type Meta, type Summary } from "./api";
import { HistoryChart } from "./HistoryChart";

const month = new Date().toISOString().slice(0, 7);
const fiveYearsAgo = `${Number(month.slice(0, 4)) - 5}-${month.slice(5)}`;
const label: Record<Measure, string> = { anual: "Anual", mensual: "Mensual", indice: "Índice" };

export function App() {
  const [measure, setMeasure] = useState<Measure>("anual");
  const [until, setUntil] = useState("");
  const [from, setFrom] = useState(fiveYearsAgo);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "empty" | "error">("loading");
  const requestId = useRef(0);
  const selectedUntil = until || summary?.periodo || month;
  const explanation = measure === "anual" ? "Cambio respecto al mismo mes del año anterior." : measure === "mensual" ? "Cambio respecto al mes anterior." : "Nivel relativo al periodo de referencia; no es un precio en pesos.";

  useEffect(() => {
    const controller = new AbortController();
    const current = ++requestId.current;
    setState("loading");
    Promise.all([getSummary(until || undefined, controller.signal), getHistory(measure, from, until || month, controller.signal)])
      .then(([nextSummary, nextHistory]) => {
        if (current !== requestId.current) return;
        setSummary(nextSummary.datos); setHistory(nextHistory.datos); setMeta(nextSummary.meta);
        setState(nextSummary.meta.estado === "sin_publicacion" || nextHistory.meta.estado === "sin_datos" ? "empty" : "ready");
      })
      .catch((error: unknown) => { if (current === requestId.current && !(error instanceof DOMException && error.name === "AbortError")) setState("error"); });
    return () => controller.abort();
  }, [measure, from, until]);

  const tableRows = useMemo(() => history.map((point) => ({ ...point, display: point.valor === null ? point.estado.replaceAll("_", " ") : `${point.valor.toFixed(2)}${measure === "indice" ? "" : "%"}` })), [history, measure]);
  return <main><header><p className="eyebrow">INEGI · México</p><h1>Laboratorio de inflación</h1><p>Consulta el índice nacional de precios y su trayectoria.</p></header>
    <section className="controls" aria-label="Controles de historia"><label>Medida<select value={measure} onChange={(event) => setMeasure(event.target.value as Measure)}>{Object.entries(label).map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select></label><label>Mes de corte<input type="month" value={until} onChange={(event) => setUntil(event.target.value)} /></label><label>Inicio de historia<input type="month" value={from} max={selectedUntil} onChange={(event) => setFrom(event.target.value)} /></label></section>
    <p className="explanation">{explanation}</p>
    {state === "loading" && <p role="status">Actualizando datos…</p>}
    {state === "error" && <p role="alert">No fue posible cargar los datos. Intenta de nuevo.</p>}
    {state === "empty" && <p role="status">Aún no hay una publicación completa disponible.</p>}
    {state === "ready" && summary && <><section className="summary" aria-label="Resumen de México"><article><span>Periodo observado</span><strong>{summary.periodo}</strong></article><article><span>Inflación anual</span><strong>{format(summary.anual)}</strong></article><article><span>Inflación mensual</span><strong>{format(summary.mensual)}</strong></article></section><section className="panel"><h2>{label[measure]} en México</h2><HistoryChart points={history} measure={measure} /><details><summary>Ver tabla de valores</summary><div className="table-wrap"><table><caption>Historia seleccionada de México</caption><thead><tr><th>Periodo</th><th>{label[measure]}</th><th>Estado</th></tr></thead><tbody>{tableRows.map((row) => <tr key={row.periodo}><td>{row.periodo}</td><td>{row.display}</td><td>{row.estado}</td></tr>)}</tbody></table></div></details></section></>}
    {meta && <footer><p>Fuente: <a href={meta.fuente_url}>INEGI</a>. Última carga: {meta.ultima_carga_exitosa ?? "sin publicación"}.</p></footer>}
  </main>;
}
function format(metric: Summary["anual"]) { return metric.valor === null ? metric.estado.replaceAll("_", " ") : `${metric.valor.toFixed(2)}${metric.unidad === "porcentaje" ? "%" : ""}`; }
