import React from 'react';
import { CloudRain, Thermometer, Droplets, Wind, AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import { NormalizedWeatherData } from '../types';

interface WeatherWidgetProps {
  weather: NormalizedWeatherData;
  farmName?: string;
  isCached?: boolean;
}

export const WeatherWidget: React.FC<WeatherWidgetProps> = ({ weather, farmName, isCached }) => {
  return (
    <div className="glass-panel-elevated rounded-2xl p-5 relative overflow-hidden">
      {/* Background glow accent */}
      <div className="absolute -right-12 -top-12 w-36 h-36 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="text-[11px] uppercase tracking-wider text-emerald-400 font-semibold flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Live Farm Microclimate
          </span>
          <h3 className="text-lg font-bold text-white mt-0.5">{farmName || 'Target Field'}</h3>
          <p className="text-xs text-slate-400">{weather.weather_description}</p>
        </div>

        {isCached ? (
          <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-1 rounded-md border border-slate-700">
            Redis Cached
          </span>
        ) : (
          <span className="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-1 rounded-md border border-emerald-600/40">
            Live Open-Meteo
          </span>
        )}
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
            <Thermometer className="w-4 h-4 text-amber-400" />
            <span>Temperature</span>
          </div>
          <span className="text-xl font-bold text-white">{weather.temperature_c.toFixed(1)}°C</span>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
            <Droplets className="w-4 h-4 text-cyan-400" />
            <span>Humidity</span>
          </div>
          <span className="text-xl font-bold text-white">{weather.relative_humidity_pct.toFixed(0)}%</span>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
            <CloudRain className="w-4 h-4 text-blue-400" />
            <span>Precipitation</span>
          </div>
          <span className="text-xl font-bold text-white">{weather.precipitation_mm.toFixed(1)} mm</span>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
            <Wind className="w-4 h-4 text-emerald-400" />
            <span>Wind Speed</span>
          </div>
          <span className="text-xl font-bold text-white">{weather.wind_speed_kmh.toFixed(1)} km/h</span>
        </div>
      </div>

      {/* Agricultural Soil Moisture & Rain Probability */}
      {(weather.soil_moisture_root_zone_m3 !== undefined || weather.precipitation_probability_pct !== undefined) && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mb-4 text-xs">
          {weather.soil_moisture_root_zone_m3 !== undefined && weather.soil_moisture_root_zone_m3 !== null && (
            <div className="bg-slate-900/40 rounded-xl px-3 py-2 border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Root Zone Soil Moisture (3-9cm)</span>
              <span className="text-sm font-bold text-emerald-300">
                {(weather.soil_moisture_root_zone_m3 * 100).toFixed(1)}% m³/m³
              </span>
            </div>
          )}
          {weather.soil_moisture_surface_m3 !== undefined && weather.soil_moisture_surface_m3 !== null && (
            <div className="bg-slate-900/40 rounded-xl px-3 py-2 border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Surface Soil Moisture (0-1cm)</span>
              <span className="text-sm font-bold text-cyan-300">
                {(weather.soil_moisture_surface_m3 * 100).toFixed(1)}% m³/m³
              </span>
            </div>
          )}
          {weather.precipitation_probability_pct !== undefined && weather.precipitation_probability_pct !== null && (
            <div className="bg-slate-900/40 rounded-xl px-3 py-2 border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Precipitation Probability</span>
              <span className="text-sm font-bold text-amber-300">
                {weather.precipitation_probability_pct.toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      )}

      {/* Epidemiological Pathogen Risk Inferences */}
      <div className="pt-3 border-t border-slate-800/80 flex flex-wrap gap-2 text-xs">
        {weather.is_risk_favorable_for_fungal && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Microclimate Favorable for Fungal Spores (RH &gt; 80%)
          </span>
        )}

        {weather.is_risk_favorable_for_bacterial && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
            Rain Splash Risk for Bacterial Spot
          </span>
        )}

        {weather.is_risk_favorable_for_vector && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-orange-500/15 text-orange-300 border border-orange-500/30">
            <Zap className="w-3.5 h-3.5 text-orange-400" />
            Dry Warm Weather Favors Whitefly Vector Migration
          </span>
        )}

        {!weather.is_risk_favorable_for_fungal && !weather.is_risk_favorable_for_bacterial && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            Normal Microclimate Conditions
          </span>
        )}
      </div>
    </div>
  );
};
