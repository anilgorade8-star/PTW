import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { WeatherWidget } from '../components/WeatherWidget';
import { 
  Sprout, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  HelpCircle, 
  BookOpen, 
  ExternalLink, 
  ArrowLeft, 
  Send,
  Sparkles,
  Layers,
  Thermometer,
  ShieldAlert,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export const AssessmentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [followupAnswer, setFollowupAnswer] = useState('');
  const [showAllCandidates, setShowAllCandidates] = useState(false);

  // Bounded Polling with TanStack Query
  const { data: assessment, isLoading, error } = useQuery({
    queryKey: ['assessment', id],
    queryFn: () => api.getAssessment(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Stop polling when completed, awaiting farmer input, or failed
      if (!data) return 2500;
      if (['completed', 'awaiting_farmer_input', 'failed'].includes(data.status)) {
        return false;
      }
      return 2500;
    }
  });

  const followupMutation = useMutation({
    mutationFn: (answer: string) => api.submitFollowup(id!, answer),
    onSuccess: () => {
      setFollowupAnswer('');
      queryClient.invalidateQueries({ queryKey: ['assessment', id] });
    }
  });

  if (isLoading) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <h3 className="text-lg font-bold text-white">Loading Assessment Data...</h3>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="py-16 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-rose-500 mx-auto" />
        <h3 className="text-xl font-bold text-white">Assessment Not Found</h3>
        <p className="text-sm text-slate-400">The assessment could not be retrieved or you do not have permission.</p>
        <Link to="/dashboard" className="inline-block px-5 py-2.5 rounded-xl bg-emerald-500 text-slate-950 font-bold text-sm">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const isQueued = assessment.status === 'queued';
  const isProcessing = assessment.status === 'processing';
  const isAwaiting = assessment.status === 'awaiting_farmer_input';
  const isCompleted = assessment.status === 'completed';
  const isFailed = assessment.status === 'failed';

  const decision = assessment.decision;
  const safety = assessment.safetyReview;
  const weather = assessment.weatherSnapshot?.normalizedData;

  return (
    <div className="max-w-6xl mx-auto py-6 space-y-8">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <Link to="/dashboard" className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <span className="text-xs font-mono text-slate-500">ID: {assessment.id}</span>
      </div>

      {/* Status Progress Banner when Queued or Processing */}
      {(isQueued || isProcessing) && (
        <div className="glass-panel-elevated rounded-3xl p-8 border border-cyan-500/30 text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400 animate-spin">
            <Clock className="w-8 h-8" />
          </div>

          <div>
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest">
              Asynchronous Background Pipeline Active
            </span>
            <h2 className="text-2xl font-extrabold text-white mt-1 font-['Outfit']">
              Executing Farm Evidence Loop
            </h2>
            <p className="text-sm text-slate-300 max-w-lg mx-auto mt-2">
              Validating image signature, querying Open-Meteo microclimate via Redis, running Gemini multimodal visual observation, and checking ICAR disease rules...
            </p>
          </div>

          {/* Stepper tracker */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 max-w-3xl mx-auto text-left text-xs pt-4 border-t border-slate-800">
            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
              <span className="text-emerald-400 font-bold block mb-1">✓ Step 1</span>
              <span>Magic Bytes & Storage Key Validated</span>
            </div>
            <div className="p-3 bg-slate-900/80 rounded-xl border border-cyan-500/30">
              <span className="text-cyan-400 font-bold block mb-1">● Step 2</span>
              <span>Microclimate Weather Ingestion</span>
            </div>
            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
              <span className="text-slate-500 font-bold block mb-1">○ Step 3</span>
              <span>Gemini Visual Symptom Extraction</span>
            </div>
            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
              <span className="text-slate-500 font-bold block mb-1">○ Step 4</span>
              <span>Deterministic Safety Engine</span>
            </div>
          </div>
        </div>
      )}

      {/* AWAITING FARMER INPUT WORKFLOW BANNER */}
      {isAwaiting && (
        <div className="glass-panel-elevated rounded-3xl p-6 sm:p-8 border border-amber-500/40 bg-amber-950/20 space-y-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
              <HelpCircle className="w-7 h-7" />
            </div>
            <div>
              <span className="text-xs font-bold text-amber-400 uppercase tracking-widest">
                Targeted Follow-up Question
              </span>
              <h2 className="text-xl sm:text-2xl font-bold text-white mt-1 font-['Outfit']">
                Clarification Required for Accurate Diagnosis
              </h2>
              <p className="text-sm text-slate-300 mt-1">
                Because visual symptoms alone can mimic multiple conditions, KrishiGuard AI does not guess blindly. Please clarify:
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-900/90 rounded-2xl border border-amber-500/30 text-amber-200 text-sm font-medium">
            "{decision?.suggestedFollowupQuestion || 'Are the dark circular lesions primarily on older bottom leaves or young shoots?'}"
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (followupAnswer.trim()) {
                followupMutation.mutate(followupAnswer.trim());
              }
            }}
            className="space-y-3"
          >
            <textarea
              required
              rows={3}
              value={followupAnswer}
              onChange={(e) => setFollowupAnswer(e.target.value)}
              placeholder="Enter your field observation here (e.g. Yes, they started on the lowest leaves near the soil, with yellow halos around the concentric rings)..."
              className="w-full px-4 py-3 rounded-2xl bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-amber-400"
            />

            <button
              type="submit"
              disabled={followupMutation.isPending || !followupAnswer.trim()}
              className="px-6 py-3 rounded-xl font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {followupMutation.isPending ? 'Re-evaluating Evidence...' : (
                <>
                  <Send className="w-4 h-4" />
                  Submit Follow-up & Re-evaluate
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* COMPLETED RESULTS DISPLAY */}
      {isCompleted && decision && (
        <div className="space-y-8">
          {/* Primary Condition Banner */}
          <div className="glass-panel-elevated rounded-3xl p-6 sm:p-8 border border-emerald-500/40 relative overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-widest text-emerald-400">
                  Primary Diagnosed Condition
                </span>
                <h1 className="text-3xl sm:text-4xl font-extrabold text-white mt-1 font-['Outfit']">
                  {decision.primaryCondition}
                </h1>
                <p className="text-sm text-slate-300 mt-1">
                  Pathogen: <span className="italic text-emerald-300 font-medium">{decision.pathogenOrStressType}</span>
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className={`px-4 py-2 rounded-2xl text-xs font-extrabold uppercase border ${
                  decision.certaintyLevel === 'high' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                  decision.certaintyLevel === 'medium' ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' :
                  'bg-amber-500/20 text-amber-300 border-amber-500/40'
                }`}>
                  {decision.certaintyLevel} Scientific Certainty
                </div>
              </div>
            </div>

            {/* Weather correlation notice */}
            <div className="mt-4 pt-4 border-t border-slate-800 text-xs text-slate-400 flex items-center gap-2">
              <Thermometer className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{decision.weatherRiskCorrelation}</span>
            </div>
          </div>

          {/* Visual Evidence & Microclimate Side-by-Side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Crop Image Display */}
            <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-['Outfit']">
                1. Crop Photograph & Visible Evidence
              </h3>
              <div className="h-64 rounded-xl bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center">
                <img
                  src={assessment.imageUrl}
                  alt="Crop foliage"
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="space-y-1.5 pt-2">
                <span className="text-[11px] font-semibold text-slate-400">Gemini Visual Observations:</span>
                <ul className="text-xs text-slate-300 space-y-1">
                  {assessment.observations.map((obs, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">•</span>
                      {obs}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Farm Microclimate Widget */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-['Outfit']">
                2. Environmental Microclimate Context
              </h3>
              {weather ? (
                <WeatherWidget
                  weather={weather}
                  farmName="Field Coordinates"
                  isCached={assessment.weatherSnapshot?.qualityMetadata?.is_cached}
                />
              ) : (
                <div className="glass-panel rounded-2xl p-6 text-center text-slate-400 text-sm">
                  Weather snapshot attached.
                </div>
              )}

              {/* Farmer Reported Symptoms */}
              <div className="glass-panel rounded-2xl p-4 border border-slate-800 text-xs space-y-2">
                <span className="font-semibold text-slate-400 block uppercase tracking-wider text-[10px]">
                  Farmer Confirmed Symptoms
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {assessment.farmerReportedSymptoms.map((s, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Actionable Farmer Plan & Agricultural Safety Barrier */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Farmer Action Plan */}
            <div className="lg:col-span-2 glass-panel-elevated rounded-2xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white font-['Outfit']">
                  Evidence-Backed Farmer Action Plan
                </h3>
              </div>

              <div className="space-y-3">
                {decision.farmerActionPlan.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-slate-900/60 rounded-xl border border-slate-800/80 text-xs sm:text-sm text-slate-200">
                    <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold flex items-center justify-center shrink-0 text-xs">
                      {idx + 1}
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Safety Review Card */}
            <div className="glass-panel-elevated rounded-2xl p-6 border border-emerald-500/30 space-y-4 bg-emerald-950/10">
              <div className="flex items-center gap-2 pb-3 border-b border-emerald-500/20 text-emerald-400 font-bold">
                <ShieldCheck className="w-5 h-5" />
                <h3 className="text-base font-['Outfit']">Safety Review</h3>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {safety?.chemicalSafetyAdvisory}
              </p>

              {safety?.warningFlags && safety.warningFlags.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs space-y-1">
                  {safety.warningFlags.map((w, i) => (
                    <div key={i} className="flex items-start gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}

              {safety?.disallowedRecommendationsFiltered && safety.disallowedRecommendationsFiltered.length > 0 && (
                <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                  <span className="text-rose-400 font-semibold block">Prohibited Advice Blocked:</span>
                  {safety.disallowedRecommendationsFiltered.map((d, i) => (
                    <span key={i} className="block line-through text-slate-500">{d}</span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Candidate Explanations (Ranked Alternatives) */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white font-['Outfit']">
                Candidate Conditions Ranked by Match Score
              </h3>
              <button
                onClick={() => setShowAllCandidates(!showAllCandidates)}
                className="text-xs text-emerald-400 font-semibold flex items-center gap-1 hover:text-emerald-300"
              >
                {showAllCandidates ? 'Show Top Only' : 'Expand All Candidates'}
                {showAllCandidates ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(showAllCandidates ? decision.candidateExplanations : decision.candidateExplanations.slice(0, 2)).map((cand, idx) => (
                <div key={idx} className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center">
                    <h4 className="text-sm font-bold text-white">{cand.commonName}</h4>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      Score: {(cand.matchScore * 100).toFixed(1)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-400">{cand.reasoning}</p>

                  {cand.supportingEvidence.length > 0 && (
                    <div className="text-[11px] text-emerald-300">
                      <span className="font-semibold block text-slate-400">Supporting Evidence:</span>
                      {cand.supportingEvidence.map((se, i) => (
                        <span key={i} className="block">• {se}</span>
                      ))}
                    </div>
                  )}

                  {cand.opposingEvidence.length > 0 && (
                    <div className="text-[11px] text-amber-300/90 pt-1">
                      <span className="font-semibold block text-slate-400">Opposing Evidence:</span>
                      {cand.opposingEvidence.map((oe, i) => (
                        <span key={i} className="block">• {oe}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Peer-Reviewed Scientific Sources */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <BookOpen className="w-5 h-5 text-emerald-400" />
              <h3 className="text-base font-bold text-white font-['Outfit']">
                Reviewed Agricultural Sources & Extension Bulletins
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {decision.sourceReferences.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noreferrer"
                  className="bg-slate-900/60 hover:bg-slate-800/60 rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex justify-between items-start gap-2 mb-1">
                      <h4 className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">
                        {src.title}
                      </h4>
                      <ExternalLink className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 shrink-0" />
                    </div>
                    <span className="text-xs text-emerald-300 font-medium block">{src.institution}</span>
                    <p className="text-[11px] text-slate-400 mt-2 line-clamp-2">
                      <strong>Limitations:</strong> {src.limitations}
                    </p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-800/80 flex justify-between items-center text-[10px] text-slate-500">
                    <span>Region: {src.region}</span>
                    <span className="text-emerald-400 uppercase font-semibold">{src.reviewStatus}</span>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Follow-up Interaction History */}
          {assessment.followups.length > 0 && (
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-['Outfit']">
                Diagnostic Interaction History
              </h3>
              <div className="space-y-3">
                {assessment.followups.map((f, i) => (
                  <div key={i} className="p-3.5 bg-slate-900/80 rounded-xl border border-slate-800 text-xs space-y-1">
                    <p className="text-amber-300 font-semibold">Q: {f.question}</p>
                    <p className="text-slate-200">A: {f.answer}</p>
                    <span className="text-[10px] text-slate-500 block pt-1">
                      {new Date(f.createdAt).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
