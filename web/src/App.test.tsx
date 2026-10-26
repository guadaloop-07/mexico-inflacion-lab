import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { App } from "./App";

vi.mock("./HistoryChart", () => ({ HistoryChart: () => <div data-testid="history-chart" /> }));

const response = (datos: unknown, estado = "disponible") => Promise.resolve(new Response(JSON.stringify({ datos, meta: { estado, fuente: "INEGI", fuente_url: "https://inegi.test", version_datos: "v1", ultima_carga_exitosa: "2026-10-01T00:00:00Z" } })));

test("muestra el resumen y cambia la medida de historia", async () => {
  const summary = { periodo: "2026-09", indice: { valor: 146, estado: "disponible", unidad: "puntos_indice" }, anual: { valor: 3.45, estado: "disponible", unidad: "porcentaje" }, mensual: { valor: 0.2, estado: "disponible", unidad: "porcentaje" } };
  globalThis.fetch = vi.fn((input) => response(String(input).includes("resumen") ? summary : [{ periodo: "2026-09", valor: 3.45, estado: "disponible" }]));
  render(<App />);
  expect((await screen.findAllByText("3.45%")).length).toBeGreaterThan(0);
  fireEvent.change(screen.getByLabelText("Medida"), { target: { value: "mensual" } });
  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledTimes(4));
});

test("explica que no hay publicación sin usar datos simulados", async () => {
  globalThis.fetch = vi.fn().mockImplementation(() => response([], "sin_publicacion"));
  render(<App />);
  expect(await screen.findByText("Aún no hay una publicación completa disponible.")).toBeInTheDocument();
});
