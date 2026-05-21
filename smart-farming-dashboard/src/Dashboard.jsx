import { createSignal, onMount, onCleanup } from 'solid-js';

export default function Dashboard() {
  // State reaktif buat nampung data dari API
  const [temperature, setTemperature] = createSignal(0);
  const [humidity, setHumidity] = createSignal(0);
  const [soilMoisture, setSoilMoisture] = createSignal(0);
  const [pumpStatus, setPumpStatus] = createSignal(false);
  
  const [tomatoCounts, setTomatoCounts] = createSignal({ raw: 0, partiallyRipe: 0, ripe: 0 });
  const [apiStatus, setApiStatus] = createSignal(true);

  // Fungsi untuk narik data dari Laravel
  const fetchDashboardData = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/dashboard');
      const json = await res.json();
      
      if (json.status === 'success') {
        const { current_sensor, current_ai } = json.data;
        
        if (current_sensor) {
          setTemperature(current_sensor.temperature);
          setHumidity(current_sensor.air_humidity);
          setSoilMoisture(current_sensor.soil_moisture);
          setPumpStatus(current_sensor.pump_status === 1);
        }
        
        if (current_ai) {
          setTomatoCounts({
            raw: current_ai.raw_count,
            partiallyRipe: current_ai.partially_ripe_count,
            ripe: current_ai.ripe_count
          });
        }
        setApiStatus(true);
      }
    } catch (error) {
      console.error("Gagal terhubung ke API Laravel:", error);
      setApiStatus(false);
    }
  };

  // Jalanin fetch pertama kali, lalu ulang tiap 3 detik (Polling)
  onMount(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 3000);
    onCleanup(() => clearInterval(interval));
  });

  return (
    <div class="bg-gray-50 text-gray-900 font-sans min-h-screen flex flex-col md:flex-row">
      
      {/* HEADER (Top Bar) */}
      <header class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-white shadow-sm border-b border-gray-200">
        <div class="flex items-center gap-2 text-green-700">
          <span class="material-symbols-outlined text-2xl font-bold" style="font-variation-settings: 'FILL' 1;">eco</span>
          <span class="text-xl font-bold">AgriPulse AI</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 bg-gray-50 px-3 py-1 rounded-full border border-gray-200">
            <div class={`w-2 h-2 rounded-full ${apiStatus() ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span class="text-xs font-semibold text-gray-600 tracking-wider">System: {apiStatus() ? 'Online' : 'Offline'}</span>
          </div>
        </div>
      </header>

      {/* KONTEN UTAMA */}
      <main class="flex-1 mt-16 p-4 md:p-8 w-full max-w-[1440px] mx-auto overflow-y-auto">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* AREA KIRI: AI Vision Panel */}
          <section class="md:col-span-2 flex flex-col gap-4">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div class="px-5 py-3 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <h2 class="text-lg font-bold text-gray-900">AI Vision Panel</h2>
                <span class="text-xs font-semibold text-gray-500 px-2 py-1 bg-gray-200 rounded uppercase tracking-wider">Live</span>
              </div>
              
              <div class="p-5">
                <div class="aspect-video bg-gray-900 rounded flex items-center justify-center relative overflow-hidden group shadow-inner">
                  <div class="absolute inset-0 flex flex-col items-center justify-center text-white">
                    <span class="material-symbols-outlined text-4xl mb-2" style="font-variation-settings: 'FILL' 1;">videocam</span>
                    <p class="text-sm tracking-wider uppercase opacity-80 font-semibold">Menunggu Stream IP Webcam...</p>
                  </div>
                </div>
                
                {/* Counter Tomat (Reaktif) */}
                <div class="grid grid-cols-3 gap-4 mt-6">
                  <div class="bg-red-50 rounded border border-red-100 p-4 flex flex-col items-center justify-center shadow-sm">
                    <span class="text-red-600 text-2xl font-bold mb-1">{tomatoCounts().ripe}</span>
                    <span class="text-xs uppercase tracking-wider font-semibold text-red-700">Ripe (Matang)</span>
                  </div>
                  <div class="bg-yellow-50 rounded border border-yellow-100 p-4 flex flex-col items-center justify-center shadow-sm">
                    <span class="text-yellow-600 text-2xl font-bold mb-1">{tomatoCounts().partiallyRipe}</span>
                    <span class="text-xs uppercase tracking-wider font-semibold text-yellow-700">Partially Ripe</span>
                  </div>
                  <div class="bg-green-50 rounded border border-green-100 p-4 flex flex-col items-center justify-center shadow-sm">
                    <span class="text-green-600 text-2xl font-bold mb-1">{tomatoCounts().raw}</span>
                    <span class="text-xs uppercase tracking-wider font-semibold text-green-700">Raw (Mentah)</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* AREA KANAN: IoT Sensor Panel (Reaktif) */}
          <section class="flex flex-col gap-4">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col overflow-hidden h-full">
              <div class="px-5 py-3 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <h2 class="text-lg font-bold text-gray-900">IoT Sensor Node</h2>
                <span class="material-symbols-outlined text-green-600">router</span>
              </div>
              
              <div class="p-5 flex flex-col gap-4 flex-grow">
                <div class="flex-1 bg-white rounded border-t-4 border-t-blue-500 border border-gray-200 p-4 flex flex-col justify-center shadow-sm">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Suhu Udara (°C)</span>
                    <span class="material-symbols-outlined text-blue-500 text-sm">thermostat</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">{temperature()}</div>
                </div>
                
                <div class="flex-1 bg-white rounded border-t-4 border-t-blue-400 border border-gray-200 p-4 flex flex-col justify-center shadow-sm">
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Kelembapan Udara (%)</span>
                    <span class="material-symbols-outlined text-blue-400 text-sm">water_drop</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">{humidity()}</div>
                </div>
                
                <div class={`flex-1 bg-white rounded border-t-4 border border-gray-200 p-4 flex flex-col justify-center shadow-sm transition-colors ${soilMoisture() < 40 ? 'border-t-red-500 bg-red-50' : 'border-t-green-500'}`}>
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Kelembapan Tanah (%)</span>
                    <span class="material-symbols-outlined text-green-600 text-sm">grass</span>
                  </div>
                  <div class={`text-2xl font-bold ${soilMoisture() < 40 ? 'text-red-600' : 'text-gray-900'}`}>{soilMoisture()}</div>
                  {soilMoisture() < 40 && (
                     <div class="text-xs font-bold text-red-600 mt-1 uppercase tracking-wider">Warning: Tanah Kering!</div>
                  )}
                </div>

                <div class={`mt-auto rounded border p-4 flex flex-col items-center justify-center transition-colors ${pumpStatus() ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}`}>
                  <div class="flex items-center gap-2 mb-2">
                    <span class={`material-symbols-outlined ${pumpStatus() ? 'text-blue-500' : 'text-gray-500'}`}>water_pump</span>
                    <span class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Pompa Air</span>
                  </div>
                  <div class={`px-4 py-2 rounded-full text-sm font-bold w-full text-center transition-all ${pumpStatus() ? 'bg-blue-500 text-white shadow-md' : 'bg-gray-300 text-gray-600'}`}>
                    Status: {pumpStatus() ? 'ON - MENYIRAM' : 'OFF'}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}