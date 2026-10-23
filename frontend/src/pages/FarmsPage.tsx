import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Farm } from '../types';
import { 
  Tractor, 
  Plus, 
  MapPin, 
  Trash2, 
  Navigation, 
  AlertCircle, 
  CheckCircle, 
  X,
  Layers
} from 'lucide-react';

export const FarmsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Form states
  const [name, setName] = useState('');
  const [latitude, setLatitude] = useState<string>('19.9975');
  const [longitude, setLongitude] = useState<string>('73.7898');
  const [district, setDistrict] = useState('Nashik');
  const [state, setState] = useState('Maharashtra');
  const [sizeInAcres, setSizeInAcres] = useState<string>('2.5');

  const { data: farms = [], isLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: () => api.listFarms()
  });

  const createMutation = useMutation({
    mutationFn: (newFarm: any) => api.createFarm(newFarm),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
      setModalOpen(false);
      resetForm();
    },
    onError: (err: any) => {
      setFormError(err?.message || 'Failed to register farm.');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (farmId: string) => api.deleteFarm(farmId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farms'] });
    }
  });

  const resetForm = () => {
    setName('');
    setLatitude('19.9975');
    setLongitude('73.7898');
    setDistrict('Nashik');
    setState('Maharashtra');
    setSizeInAcres('2.5');
    setFormError(null);
  };

  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      setFormError('Geolocation is not supported by your browser.');
      return;
    }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(pos.coords.latitude.toFixed(4));
        setLongitude(pos.coords.longitude.toFixed(4));
        setGeoLoading(false);
      },
      (err) => {
        setFormError('Could not retrieve browser coordinates. You can enter them manually.');
        setGeoLoading(false);
      }
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const latNum = parseFloat(latitude);
    const lonNum = parseFloat(longitude);

    if (isNaN(latNum) || isNaN(lonNum)) {
      setFormError('Please enter valid numerical latitude and longitude.');
      return;
    }

    createMutation.mutate({
      name,
      location: {
        latitude: latNum,
        longitude: lonNum,
        district,
        state,
        address: `${district}, ${state}`
      },
      cropTypes: ['tomato'],
      sizeInAcres: sizeInAcres ? parseFloat(sizeInAcres) : undefined
    });
  };

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <span className="text-xs uppercase font-bold tracking-widest text-emerald-400">Land & Microclimate Registry</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1 font-['Outfit']">My Registered Farms</h1>
          <p className="text-sm text-slate-400 mt-0.5">Manage farm locations to link local Open-Meteo microclimate weather to assessments</p>
        </div>

        <button
          onClick={() => { resetForm(); setModalOpen(true); }}
          className="px-4 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20 transition-all hover:scale-102 flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          Register New Farm
        </button>
      </div>

      {/* Farm Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(n => (
            <div key={n} className="h-44 rounded-2xl bg-slate-900/60 animate-pulse border border-slate-800" />
          ))}
        </div>
      ) : farms.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
          <Tractor className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-white">No registered farms</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
            Add your farm's geographic coordinates so that KrishiGuard can automatically pull local microclimate risk parameters during diagnostic runs.
          </p>
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 text-slate-950 mt-5 hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/20"
          >
            <Plus className="w-4 h-4 stroke-[3]" />
            Register Your First Farm
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {farms.map((farm: Farm) => (
            <div
              key={farm.id}
              className="glass-panel-elevated rounded-2xl p-5 border border-slate-800/90 hover:border-emerald-500/40 transition-all relative flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                      <Tractor className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">{farm.name}</h3>
                      <span className="text-[11px] text-slate-400">{farm.cropTypes.join(', ')}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      if (window.confirm(`Are you sure you want to delete ${farm.name}?`)) {
                        deleteMutation.mutate(farm.id);
                      }
                    }}
                    className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                    title="Delete Farm"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-2 text-xs text-slate-300 mt-4 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span className="truncate">{farm.location.district || 'Rural Sector'}, {farm.location.state || 'India'}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 pl-5">
                    GPS: {farm.location.latitude.toFixed(4)}°N, {farm.location.longitude.toFixed(4)}°E
                  </div>
                  {farm.sizeInAcres && (
                    <div className="flex items-center gap-2 text-slate-400 pt-1 border-t border-slate-800/60">
                      <Layers className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                      <span>{farm.sizeInAcres} Acres</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex justify-between items-center text-[11px] text-slate-500">
                <span>Registered on {new Date(farm.createdAt).toLocaleDateString()}</span>
                <span className="text-emerald-400 font-medium">Active Monitoring</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Register Farm Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
          <div className="glass-panel-elevated w-full max-w-lg rounded-3xl p-6 sm:p-8 border border-emerald-500/30 relative">
            <button
              onClick={() => setModalOpen(false)}
              className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Tractor className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white font-['Outfit']">Register New Farm</h3>
                <p className="text-xs text-slate-400">Coordinates are used for localized Open-Meteo weather caching</p>
              </div>
            </div>

            {formError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
                  Farm Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. North Ridge Tomato Block"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              {/* Location button */}
              <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-slate-300">GPS Coordinates</span>
                  <button
                    type="button"
                    onClick={handleGetLocation}
                    disabled={geoLoading}
                    className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-semibold hover:text-emerald-300 bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-600/30"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    {geoLoading ? 'Detecting...' : 'Detect Current GPS'}
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-0.5">Latitude (°N)</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={latitude}
                      onChange={(e) => setLatitude(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-0.5">Longitude (°E)</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={longitude}
                      onChange={(e) => setLongitude(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
                    District
                  </label>
                  <input
                    type="text"
                    required
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
                    State
                  </label>
                  <input
                    type="text"
                    required
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
                  Farm Size in Acres
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={sizeInAcres}
                  onChange={(e) => setSizeInAcres(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="pt-3 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-6 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-md shadow-emerald-500/20 transition-all flex items-center gap-2"
                >
                  {createMutation.isPending ? 'Registering...' : 'Register Farm'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
