import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import type { HistoryPoint, Measure } from "./api";

export function HistoryChart({ points, measure }: { points: HistoryPoint[]; measure: Measure }) {
  const element = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!element.current) return;
    const chart = echarts.init(element.current);
    const title = measure === "indice" ? "Índice" : measure === "anual" ? "Variación anual" : "Variación mensual";
    chart.setOption({
      aria: { enabled: true, description: `${title} de México a través del tiempo.` },
      grid: { left: 58, right: 24, top: 34, bottom: 58 },
      tooltip: { trigger: "axis", valueFormatter: (value: number) => `${value.toFixed(2)}${measure === "indice" ? "" : "%"}` },
      xAxis: { type: "category", data: points.map((point) => point.periodo), axisLabel: { rotate: 45 } },
      yAxis: { type: "value", name: measure === "indice" ? "Puntos" : "Porcentaje" },
      series: [{ type: "line", connectNulls: false, showSymbol: false, data: points.map((point) => point.valor), color: "#007a78" }],
    });
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(element.current);
    return () => { observer.disconnect(); chart.dispose(); };
  }, [measure, points]);
  return <div className="chart" ref={element} aria-label="Gráfica de historia de inflación" />;
}
