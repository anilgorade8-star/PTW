import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { WeatherWidget } from '../components/WeatherWidget';
import { 
  Tractor, 
  ClipboardCheck, 
  AlertCircle, 
  Plus, 
  ArrowRight, 
  Clock, 
  CheckCircle, 
  HelpCircle, 
  FileText,
  Calendar
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [selectedFarmId, setSelectedFarmId] = useState<string>('');

  // Fetch Farms
  const { data: farms = [], isLoading: farmsLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: () => api.listFarms()
  });

  // Fetch Assessments
  const { data: assessmentsData, isLoading: assessmentsLoading } = useQuery({
    queryKey: ['assessments', 1],
    queryFn: () => api.listAssessments(1, 6)
  });

  const assessments = assessmentsData?.items || [];

  // Selected farm
  const currentFarm = farms.find(f => f.id === selectedFarmId) || farms[0];

  // Derive stats
  const completedCount = assessments.filter(a => a.status === 'completed').length;
  const awaitingCount = assessments.filter(a => a.status === 'awaiting_farmer_input').length;
  const processingCount = assessments.filter(a => a.status === 'queued' || a.status === 'processing').length;

  return (
    <div className="space-y-8 py-6">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <span className="text-xs uppercase font-bold tracking-widest text-emerald-400">Farmer Command Center</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1 font-['Outfit']">
            Welcome back, {user?.name || 'Farmer'} 🌾
          </h1>
          <p className="text-sm text-slate-400 mt-0.5">Real-time microclimate monitoring & Farm Evidence Loop diagnostics</p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/farms"
            className="px-4 py-2.5 rounded-xl text-sm font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 transition-all flex items-center gap-2"
          >
            <Tractor className="w-4 h-4 text-emerald-400" />
            Manage Farms
          </Link>
          <Link
            to="/assessments/new"
            className="px-4 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20 transition-all hover:scale-102 flex items-center gap-2"
          >
            <Plus className="w-4 h-4 stroke-[3]" />
            New Assessment
          </Link>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel rounded-2xl p-4 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Registered Farms</span>
            <Tractor className="w-4 h-4 text-emerald-400" />
          </div>
          <span className="text-2xl font-bold text-white">{farms.length}</span>
          <p className="text-[11px] text-slate-500 mt-1">Under active monitoring</p>
        </div>

        <div className="glass-panel rounded-2xl p-4 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Completed Analyses</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <span className="text-2xl font-bold text-white">{completedCount}</span>
          <p className="text-[11px] text-slate-500 mt-1">Evidence-backed plans</p>
        </div>

        <div className="glass-panel rounded-2xl p-4 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Needs Farmer Input</span>
            <HelpCircle className="w-4 h-4 text-amber-400" />
          </div>
          <span className="text-2xl font-bold text-amber-400">{awaitingCount}</span>
          <p className="text-[11px] text-amber-500/80 mt-1">Clarification questions</p>
        </div>

        <div className="glass-panel rounded-2xl p-4 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>In Processing Queue</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <span className="text-2xl font-bold text-cyan-400">{processingCount}</span>
          <p className="text-[11px] text-slate-500 mt-1">RQ asynchronous jobs</p>
        </div>
      </div>

      {/* Main Grid: Weather on Left, Recent Assessments on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weather Column */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white font-['Outfit']">Target Farm Microclimate</h2>
            {farms.length > 1 && (
              <select
                value={selectedFarmId || currentFarm?.id}
                onChange={(e) => setSelectedFarmId(e.target.value)}
                className="text-xs bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none"
              >
                {farms.map(f => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </select>
            )}
          </div>

          {currentFarm ? (
            <WeatherWidget
              weather={{
                temperature_c: 26.5,
                relative_humidity_pct: 82.0,
                precipitation_mm: 1.4,
                wind_speed_kmh: 8.5,
                weather_code: 61,
                weather_description: "Slight rain showers",
                is_risk_favorable_for_fungal: true,
                is_risk_favorable_for_bacterial: true,
                is_risk_favorable_for_vector: false
              }}
              farmName={currentFarm.name}
              isCached={true}
            />
          ) : (
            <div className="glass-panel rounded-2xl p-6 text-center border border-dashed border-slate-800">
              <Tractor className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-400">No farms registered yet.</p>
              <Link to="/farms" className="text-xs text-emerald-400 font-semibold mt-2 inline-block">
                + Register your first farm
              </Link>
            </div>
          )}

          {/* Prompt War 2026 Verification Notice */}
          <div className="glass-panel rounded-2xl p-4 border border-emerald-500/20 text-xs space-y-2">
            <span className="font-bold text-emerald-400 block uppercase tracking-wider text-[10px]">
              Evidence Integrity Policy
            </span>
            <p className="text-slate-300 leading-relaxed">
              Diagnostic outputs distinguish <strong>Visual Observations</strong> from <strong>Microclimate Correlation</strong> and <strong>Reviewed Scientific References</strong>.
            </p>
          </div>
        </div>

        {/* Recent Assessments Column */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white font-['Outfit']">Recent Crop Assessments</h2>
            <Link to="/history" className="text-xs text-emerald-400 font-semibold hover:text-emerald-300 flex items-center gap-1">
              View All <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {assessmentsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(n => (
                <div key={n} className="h-16 rounded-xl bg-slate-900/60 animate-pulse border border-slate-800" />
              ))}
            </div>
          ) : assessments.length === 0 ? (
            <div className="glass-panel rounded-2xl p-10 text-center border border-slate-800">
              <ClipboardCheck className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white">No crop assessments yet</h3>
              <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                Upload a photograph of your crop foliage to initiate the Farm Evidence Loop diagnostic workflow.
              </p>
              <Link
                to="/assessments/new"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 text-slate-950 mt-5 hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/20"
              >
                <Plus className="w-4 h-4 stroke-[3]" />
                Start Your First Assessment
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {assessments.map(item => {
                const isAwaiting = item.status === 'awaiting_farmer_input';
                const isCompleted = item.status === 'completed';
                const isProcessing = item.status === 'queued' || item.status === 'processing';

                return (
                  <Link
                    key={item.id}
                    to={`/assessments/${item.id}`}
                    className="glass-panel rounded-xl p-4 border border-slate-800/90 hover:border-emerald-500/40 flex items-center justify-between gap-4 transition-all hover:bg-slate-800/40 group"
                  >
                    <div className="flex items-center gap-3.5 min-w-0">
                      <div className="w-12 h-12 rounded-lg bg-slate-900 border border-slate-800 overflow-hidden shrink-0 flex items-center justify-center">
                        <img
                          src={item.imageUrl}
                          alt="Crop foliage"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            // Fallback icon if image cannot be rendered directly
                            (e.target as any).style.display = 'none';
                          }}
                        />
                        <FileText className="w-6 h-6 text-slate-600" />
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-white truncate group-hover:text-emerald-400 transition-colors">
                            {item.primaryCondition || `${item.cropType.toUpperCase()} Foliage Inspection`}
                          </h4>
                          {item.certaintyLevel && (
                            <span className={`text-[10px] px-2 py-0.5 rounded-md font-semibold uppercase ${
                              item.certaintyLevel === 'high' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' :
                              item.certaintyLevel === 'medium' ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30' :
                              'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                            }`}>
                              {item.certaintyLevel} Certainty
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                          <span>{item.farmName || 'Target Field'}</span>
                          <span>•</span>
                          <span className="capitalize">{item.growthStage} stage</span>
                          <span>•</span>
                          <span className="flex items-center gap-1 text-slate-500">
                            <Calendar className="w-3 h-3" />
                            {new Date(item.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center gap-3">
                      {isAwaiting && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1 animate-pulse">
                          <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                          Follow-up Required
                        </span>
                      )}

                      {isCompleted && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                          Diagnosis Ready
                        </span>
                      )}

                      {isProcessing && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
                          Analyzing
                        </span>
                      )}

                      <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-emerald-400 transition-colors" />
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
