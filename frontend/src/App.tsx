import { useQuery } from "@tanstack/react-query";
import { api } from "./services/api";

export default function App() {
  const { data: health } = useQuery({ queryKey: ["health"], queryFn: api.health });
  const { data: cameras, isLoading } = useQuery({ queryKey: ["cameras"], queryFn: api.listCameras });

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">DRASHTI (દ્રષ્ટિ)</h1>
        <p className="text-slate-400 text-sm">
          Digital Registry And Surveillance Tracking Hub for Investigation — backend:{" "}
          {health ? health.status : "connecting..."}
        </p>
      </header>

      <section>
        <h2 className="text-lg font-semibold mb-2">Camera Registry (sample data)</h2>
        {isLoading && <p className="text-slate-400">Loading cameras...</p>}
        <ul className="space-y-2">
          {cameras?.map((c) => (
            <li key={c.id} className="rounded border border-slate-700 p-3 bg-slate-800">
              <div className="font-medium">{c.name}</div>
              <div className="text-xs text-slate-400">
                {c.department} · {c.camera_type} · {c.status} · ({c.lat}, {c.lon})
              </div>
            </li>
          ))}
        </ul>
        <p className="text-xs text-slate-500 mt-4">
          Next: replace this list with the Leaflet GIS map (docs/05_ROADMAP_7DAY.md, Day 2).
        </p>
      </section>
    </div>
  );
}
