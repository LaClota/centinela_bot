import { useState, useEffect } from 'react'

interface Camera {
  id: string;
  name: string;
  status: string;
}

function App() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [systemStatus, setSystemStatus] = useState('online');

  const API_BASE = import.meta.env.DEV ? 'http://100.119.235.64:8000' : '/api';

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await fetch(`${API_BASE}/cameras`);
        if (!response.ok) throw new Error("Backend reachable but returned error");
        const data = await response.json();
        setCameras(data);
        setSystemStatus('online');
      } catch (error) {
        console.error("Error fetching cameras:", error);
        setSystemStatus('offline');
      }
    };

    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-500/30">

      {/* Top Navigation Bar */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-white/10 px-6 py-4 flex justify-between items-center shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/30">
            <span className="text-2xl">🛡️</span>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white leading-tight">Centinela <span className="text-blue-400">Security</span></h1>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Monitoring Station</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* System Status Pill */}
          <div className={`px-3 py-1.5 rounded-full border flex items-center gap-2 transition-all shadow-lg ${systemStatus === 'online' ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' : 'border-rose-500/30 bg-rose-500/10 text-rose-400'}`}>
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${systemStatus === 'online' ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${systemStatus === 'online' ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
            </span>
            <span className="text-xs font-bold tracking-wider">{systemStatus === 'online' ? 'SYSTEM ONLINE' : 'DISCONNECTED'}</span>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="p-6 max-w-[1920px] mx-auto grid grid-cols-1 xl:grid-cols-4 gap-6">

        {/* Camera Grid (Main Focus) */}
        <section className="xl:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-slate-200 flex items-center gap-2">
              <span className="bg-slate-800 p-1.5 rounded text-slate-400">📹</span> Live Feeds
            </h2>
            <div className="text-xs font-mono text-slate-500">
              {cameras.length} Active Sources
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-3 gap-4">
            {cameras.length > 0 ? cameras.map((cam) => (
              <div key={cam.id} className="group relative bg-black/60 rounded-xl overflow-hidden border border-white/10 shadow-xl transition-all hover:border-blue-500/30 hover:shadow-blue-900/10 aspect-video flex items-center justify-center">

                {/* Status Indicator (Top Right) */}
                <div className="absolute top-3 right-3 z-20 flex items-center gap-1.5 bg-black/60 backdrop-blur px-2 py-1 rounded-md border border-white/5">
                  <div className={`w-1.5 h-1.5 rounded-full ${cam.status === 'connected' ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
                  <span className={`text-[10px] font-bold tracking-wider ${cam.status === 'connected' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {cam.status === 'connected' ? 'LIVE' : 'LOST'}
                  </span>
                </div>

                {/* Camera Name (Bottom Left) */}
                <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent z-20">
                  <p className="text-sm font-medium text-white shadow-sm flex items-center gap-2">
                    {cam.name}
                    <span className="text-[10px] text-slate-400 font-mono opacity-60">ID: {cam.id}</span>
                  </p>
                </div>

                {/* Video Image - Using object-contain to prevent stretching */}
                <img
                  src={`${API_BASE}/cameras/${cam.id}/stream?t=${Date.now()}`}
                  alt={cam.name}
                  className="w-full h-full object-contain bg-black/40"
                  loading="eager"
                  onError={(e) => {
                    const target = e.currentTarget;
                    target.style.display = 'none'; // Hide broken image
                    const parent = target.parentElement;
                    if (parent) {
                      const placeholder = parent.querySelector('.placeholder-state');
                      if (placeholder) (placeholder as HTMLElement).classList.remove('hidden');
                    }
                  }}
                />

                {/* Offline/Error Placeholder */}
                <div className="placeholder-state hidden absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm z-10">
                  <div className="p-4 rounded-full bg-slate-800/50 mb-3 animate-pulse">
                    <span className="text-3xl grayscale opacity-50">📡</span>
                  </div>
                  <p className="text-sm text-slate-400 font-medium">Signal Lost</p>
                  <p className="text-xs text-slate-600 mt-1">Check Connection</p>
                </div>

              </div>
            )) : (
              // Empty State
              <div className="col-span-full h-96 flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-2xl bg-slate-900/20">
                <div className="text-4xl mb-4 opacity-50">🔭</div>
                <p className="text-slate-400 font-medium">Scanning for cameras...</p>
                <div className="mt-4 flex gap-1">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Info Sidebar */}
        <aside className="space-y-6">
          {/* System Health Card */}
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/5 rounded-xl p-5 shadow-xl">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
              <span className="w-1 h-4 bg-blue-500 rounded-full"></span> System Health
            </h3>

            <div className="space-y-5">
              {/* Storage */}
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">VM Storage</span>
                  <span className="text-blue-400 font-mono">45%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500/80 w-[45%]"></div>
                </div>
              </div>

              {/* Network Pings */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800/50 p-3 rounded-lg border border-white/5">
                  <p className="text-[10px] text-slate-500 mb-1">Backend Latency</p>
                  <p className="text-lg font-mono text-emerald-400">12<span className="text-xs text-slate-600 ml-1">ms</span></p>
                </div>
                <div className="bg-slate-800/50 p-3 rounded-lg border border-white/5">
                  <p className="text-[10px] text-slate-500 mb-1">RPi Link</p>
                  <p className="text-lg font-mono text-emerald-400">OK</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-slate-900/50 backdrop-blur-md border border-white/5 rounded-xl p-5 shadow-xl">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
              <span className="w-1 h-4 bg-purple-500 rounded-full"></span> Controls
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <button className="p-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors border border-indigo-400/20 active:scale-95">
                📸 Snapshot
              </button>
              <button className="p-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors border border-white/5 active:scale-95">
                🔄 Reboot UI
              </button>
            </div>
            <p className="text-[10px] text-center mt-3 text-slate-600">Administrative Access Only</p>
          </div>
        </aside>

      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 w-full text-center py-2 text-[10px] text-slate-600 bg-slate-950/80 backdrop-blur-sm pointer-events-none">
        Centinela v1.0.2 • Secure Connection • 100.119.235.64
      </footer>

    </div>
  )
}

export default App

