import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api';
import { 
  Upload, 
  Sprout, 
  Tractor, 
  AlertCircle, 
  Check, 
  HelpCircle, 
  ArrowRight,
  ImageIcon,
  Sparkles
} from 'lucide-react';

const COMMON_SYMPTOMS = [
  "Dark concentric rings / target board spots",
  "Yellow halo around leaf spots",
  "Lower foliage affected first",
  "Water-soaked dark lesions",
  "Upward curling & cupping of leaf edges",
  "Stunted plant growth",
  "Olive-green velvety mold on underside",
  "Tiny angular black specks with ragged center",
  "Healthy green foliage"
];

const GROWTH_STAGES = [
  { id: 'seedling', label: 'Seedling / Nursery' },
  { id: 'vegetative', label: 'Vegetative Growth' },
  { id: 'flowering', label: 'Flowering Stage' },
  { id: 'fruiting', label: 'Fruiting / Berry Development' },
  { id: 'harvest', label: 'Harvest Stage' },
];

export const NewAssessmentPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: farms = [], isLoading: farmsLoading } = useQuery({
    queryKey: ['farms'],
    queryFn: () => api.listFarms()
  });

  const [farmId, setFarmId] = useState('');
  const [cropType, setCropType] = useState('tomato');
  const [growthStage, setGrowthStage] = useState('vegetative');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [customSymptom, setCustomSymptom] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const toggleSymptom = (s: string) => {
    setSelectedSymptoms(prev => 
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    );
  };

  const handleFileChange = (file: File) => {
    setError(null);
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Please upload a JPEG, PNG, or WebP image.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('File exceeds 5MB limit. Please choose a smaller photo.');
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  // Helper to load realistic sample canvas images for instant testing
  const generateSampleImage = (type: string, symptomsText: string[]) => {
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Background leaf color
    ctx.fillStyle = type === 'healthy' ? '#15803d' : '#14532d';
    ctx.fillRect(0, 0, 400, 400);

    // Draw stylized leaf veins
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(200, 380);
    ctx.lineTo(200, 30);
    ctx.moveTo(200, 280);
    ctx.lineTo(80, 200);
    ctx.moveTo(200, 200);
    ctx.lineTo(320, 140);
    ctx.moveTo(200, 120);
    ctx.lineTo(100, 80);
    ctx.stroke();

    if (type === 'early_blight') {
      // Draw concentric bullseye spots
      ctx.fillStyle = '#78350f';
      ctx.beginPath();
      ctx.arc(140, 180, 40, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ca8a04';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(140, 180, 25, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(140, 180, 10, 0, Math.PI * 2);
      ctx.stroke();
    } else if (type === 'late_blight') {
      // Water-soaked brownish black patches
      ctx.fillStyle = '#1c1917';
      ctx.beginPath();
      ctx.ellipse(220, 160, 60, 40, 0.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#e2e8f0';
      ctx.globalAlpha = 0.4;
      ctx.beginPath();
      ctx.arc(240, 170, 20, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1.0;
    } else if (type === 'yellow_leaf_curl') {
      // Yellow chlorotic edges
      ctx.fillStyle = '#eab308';
      ctx.beginPath();
      ctx.arc(80, 80, 60, 0, Math.PI * 2);
      ctx.fill();
    }

    canvas.toBlob((blob) => {
      if (blob) {
        const testFile = new File([blob], `${type}_test_sample.jpg`, { type: 'image/jpeg' });
        handleFileChange(testFile);
        setSelectedSymptoms(symptomsText);
      }
    }, 'image/jpeg');
  };

  const createMutation = useMutation({
    mutationFn: (formData: FormData) => api.createAssessment(formData),
    onSuccess: (data) => {
      navigate(`/assessments/${data.id}`);
    },
    onError: (err: any) => {
      setError(err?.message || 'Failed to submit assessment.');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const activeFarmId = farmId || (farms.length > 0 ? farms[0].id : '');
    if (!activeFarmId) {
      setError('Please select or register a farm first.');
      return;
    }
    if (!selectedFile) {
      setError('Please upload or generate a crop leaf photograph.');
      return;
    }

    const allSymptoms = [...selectedSymptoms];
    if (customSymptom.trim()) {
      allSymptoms.push(customSymptom.trim());
    }

    const fd = new FormData();
    fd.append('image', selectedFile);
    fd.append('farmId', activeFarmId);
    fd.append('cropType', cropType);
    fd.append('growthStage', growthStage);
    fd.append('symptoms', JSON.stringify(allSymptoms));

    createMutation.mutate(fd);
  };

  return (
    <div className="max-w-4xl mx-auto py-6 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <span className="text-xs uppercase font-bold tracking-widest text-emerald-400">Farm Evidence Loop</span>
        <h1 className="text-3xl font-extrabold text-white mt-1 font-['Outfit']">New Crop Assessment</h1>
        <p className="text-sm text-slate-400 mt-1">
          Combine crop photography, growth stage, and local microclimate for verified ICAR diagnosis
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {farms.length === 0 && !farmsLoading && (
        <div className="glass-panel rounded-2xl p-6 text-center border border-amber-500/30 bg-amber-950/10">
          <AlertCircle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
          <h3 className="text-base font-bold text-white">No Registered Farms Found</h3>
          <p className="text-xs text-slate-400 mt-1">
            You must register a farm location first so the system can retrieve live Open-Meteo microclimate weather for this assessment.
          </p>
          <Link
            to="/farms"
            className="inline-block mt-4 px-5 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-all"
          >
            + Register Farm Now
          </Link>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Farm and Crop Stage */}
        <div className="glass-panel-elevated rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Tractor className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-bold text-white font-['Outfit']">1. Farm & Crop Stage</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Target Farm
              </label>
              <select
                required
                value={farmId || (farms[0]?.id || '')}
                onChange={(e) => setFarmId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
              >
                {farms.map(f => (
                  <option key={f.id} value={f.id}>{f.name} ({f.location.district || 'Field'})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Crop
              </label>
              <input
                type="text"
                disabled
                value="Tomato (Solanum lycopersicum)"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-emerald-300 text-sm font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Plant Growth Stage
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {GROWTH_STAGES.map(stage => {
                const isSelected = growthStage === stage.id;
                return (
                  <button
                    type="button"
                    key={stage.id}
                    onClick={() => setGrowthStage(stage.id)}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold transition-all border ${
                      isSelected
                        ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-md shadow-emerald-500/20'
                        : 'bg-slate-900/80 text-slate-300 border-slate-700 hover:border-slate-500'
                    }`}
                  >
                    {stage.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Step 2: Upload Photo */}
        <div className="glass-panel-elevated rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-emerald-400" />
              <h3 className="text-base font-bold text-white font-['Outfit']">2. Crop Photograph</h3>
            </div>
            <span className="text-[11px] text-slate-400">JPEG, PNG, or WebP &lt; 5MB</span>
          </div>

          {/* Quick Demo Test Buttons */}
          <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Instant Test Samples (Click to simulate realistic leaf foliage):</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => generateSampleImage('early_blight', [
                  "Dark concentric rings / target board spots",
                  "Yellow halo around leaf spots",
                  "Lower foliage affected first"
                ])}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium"
              >
                🎯 Early Blight Sample
              </button>
              <button
                type="button"
                onClick={() => generateSampleImage('late_blight', [
                  "Water-soaked dark lesions",
                  "Lower foliage affected first"
                ])}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium"
              >
                🌧️ Late Blight Sample
              </button>
              <button
                type="button"
                onClick={() => generateSampleImage('yellow_leaf_curl', [
                  "Upward curling & cupping of leaf edges",
                  "Stunted plant growth"
                ])}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium"
              >
                🦟 Yellow Leaf Curl Sample
              </button>
              <button
                type="button"
                onClick={() => generateSampleImage('healthy', [
                  "Healthy green foliage"
                ])}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium"
              >
                🌱 Healthy Foliage Sample
              </button>
            </div>
          </div>

          {/* Drag & Drop Zone */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
            <label className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-2xl cursor-pointer bg-slate-900/40 hover:bg-slate-900/80 transition-all p-4 text-center">
              <Upload className="w-8 h-8 text-slate-500 mb-2" />
              <span className="text-xs font-semibold text-white">Click to upload crop photograph</span>
              <span className="text-[11px] text-slate-500 mt-1">or drag and drop leaf photo here</span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileChange(e.target.files[0]);
                  }
                }}
              />
            </label>

            {/* Preview Box */}
            <div className="h-48 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden relative">
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
              ) : (
                <div className="text-center text-slate-600">
                  <ImageIcon className="w-8 h-8 mx-auto mb-1" />
                  <span className="text-xs">No image selected yet</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Step 3: Farmer Reported Symptoms */}
        <div className="glass-panel-elevated rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Sprout className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-bold text-white font-['Outfit']">3. Observed Symptoms (Context)</h3>
          </div>

          <p className="text-xs text-slate-400">
            Select any symptoms you observe in your field. This prevents misclassifying diseases that look alike on camera:
          </p>

          <div className="flex flex-wrap gap-2">
            {COMMON_SYMPTOMS.map((s, i) => {
              const active = selectedSymptoms.includes(s);
              return (
                <button
                  type="button"
                  key={i}
                  onClick={() => toggleSymptom(s)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 border ${
                    active
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {active && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                  {s}
                </button>
              );
            })}
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              Additional Notes or Observations
            </label>
            <textarea
              rows={2}
              value={customSymptom}
              onChange={(e) => setCustomSymptom(e.target.value)}
              placeholder="e.g. Started after 3 days of morning fog; spots did not spread to green fruit yet..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={createMutation.isPending || farms.length === 0}
          className="w-full py-4 rounded-2xl font-extrabold text-base bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-xl shadow-emerald-500/25 transition-all hover:scale-101 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {createMutation.isPending ? (
            <>
              <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Launching Farm Evidence Loop Pipeline...</span>
            </>
          ) : (
            <>
              <span>Run Scientific Assessment</span>
              <ArrowRight className="w-5 h-5 stroke-[2.5]" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
