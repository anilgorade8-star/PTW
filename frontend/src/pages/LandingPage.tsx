import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Sprout, 
  ShieldCheck, 
  CloudRain, 
  BookOpen, 
  HelpCircle, 
  CheckCircle2, 
  ArrowRight, 
  Cpu, 
  Lock, 
  AlertOctagon,
  Eye,
  FileCheck,
  Zap
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { loginDemo } = useAuth();
  const navigate = useNavigate();
  const [demoLoading, setDemoLoading] = useState(false);

  const handleDemoClick = async () => {
    setDemoLoading(true);
    try {
      await loginDemo();
      navigate('/dashboard');
    } catch {
      navigate('/login');
    } finally {
      setDemoLoading(false);
    }
  };

  const steps = [
    { icon: Eye, title: "1. Visual Observation", desc: "Farmer captures crop photograph. Gemini AI inspects leaf symptoms without hallucinating unverified dosages." },
    { icon: CloudRain, title: "2. Farm Microclimate", desc: "Live weather from Open-Meteo cached in Redis checks if temperature and humidity favor pathogen sporulation." },
    { icon: BookOpen, title: "3. ICAR Scientific Backing", desc: "Validated against peer-reviewed plant pathology bulletins from ICAR, TNAU, PAU, and state extension services." },
    { icon: Cpu, title: "4. Deterministic Rules", desc: "Rule engine weighs symptoms, growth stage, and contradictions. Asks targeted follow-ups if confidence is ambiguous." },
    { icon: ShieldCheck, title: "5. Agricultural Safety Barrier", desc: "Filters hazardous chemical cocktails and unapproved antibiotics. Mandates statutory PPE and Pre-Harvest Intervals." }
  ];

  return (
    <div className="space-y-24 py-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-8 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider mb-6 animate-pulse-slow">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            The Farm Evidence Loop Framework
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight font-['Outfit']">
            AI Crop Decision Support Powered by <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-lime-300">Agricultural Science</span>, Not Guesswork.
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            A single photo is not enough to diagnose a crop disease. KrishiGuard AI combines visual symptoms, farm weather, ICAR research, and safety barriers to give farmers trustworthy recommendations.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={handleDemoClick}
              disabled={demoLoading}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-slate-950 shadow-xl shadow-amber-500/25 transition-all hover:scale-105 flex items-center justify-center gap-2"
            >
              {demoLoading ? (
                <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Zap className="w-5 h-5 fill-current stroke-[2.5]" />
                  ⚡ Try Live Demo (1-Click)
                </>
              )}
            </button>
            <Link
              to="/register"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-xl shadow-emerald-500/25 transition-all hover:scale-105 flex items-center justify-center gap-2"
            >
              Start Crop Assessment
              <ArrowRight className="w-5 h-5 stroke-[2.5]" />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold bg-slate-800/80 hover:bg-slate-700/80 text-white border border-slate-700/80 transition-all flex items-center justify-center gap-2"
            >
              Sign In
            </Link>
          </div>

          {/* Quick stats / guarantees */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
            <div className="glass-panel rounded-xl p-4 border border-emerald-900/40">
              <span className="text-2xl font-extrabold text-emerald-400">100%</span>
              <p className="text-xs text-slate-400 mt-1">Verified ICAR & University Protocols</p>
            </div>
            <div className="glass-panel rounded-xl p-4 border border-emerald-900/40">
              <span className="text-2xl font-extrabold text-cyan-400">0.0</span>
              <p className="text-xs text-slate-400 mt-1">Speculative Toxic Chemical Dosages</p>
            </div>
            <div className="glass-panel rounded-xl p-4 border border-emerald-900/40">
              <span className="text-2xl font-extrabold text-amber-400">Redis</span>
              <p className="text-xs text-slate-400 mt-1">Atomic Rate Limits & Microclimate Cache</p>
            </div>
            <div className="glass-panel rounded-xl p-4 border border-emerald-900/40">
              <span className="text-2xl font-extrabold text-lime-400">Argon2id</span>
              <p className="text-xs text-slate-400 mt-1">Enterprise Credential Security</p>
            </div>
          </div>
        </div>
      </section>

      {/* The Farm Evidence Loop Workflow */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Architectural Advantage</span>
          <h2 className="text-3xl font-extrabold text-white mt-2 font-['Outfit']">How the Farm Evidence Loop Works</h2>
          <p className="text-slate-400 mt-3 text-sm">
            Standard classifiers fail when two diseases show similar spots. KrishiGuard AI correlates multiple streams of truth before arriving at a decision.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {steps.map((st, i) => {
            const Icon = st.icon;
            return (
              <div key={i} className="glass-panel rounded-2xl p-5 border border-slate-800 hover:border-emerald-500/40 transition-colors relative group">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-110 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white mb-2">{st.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{st.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Comparison: Generic Chatbot vs KrishiGuard AI */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-panel-elevated rounded-3xl p-8 border border-emerald-500/30 overflow-hidden">
          <div className="text-center max-w-2xl mx-auto mb-8">
            <h2 className="text-2xl font-bold text-white font-['Outfit']">The Critical Difference</h2>
            <p className="text-slate-400 text-sm mt-1">Why deterministic safety rules prevent catastrophic agricultural mistakes.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-rose-950/20 border border-rose-900/40 rounded-2xl p-6">
              <div className="flex items-center gap-2 text-rose-400 font-bold mb-4">
                <AlertOctagon className="w-5 h-5" />
                <span>Typical AI Photo Classifiers</span>
              </div>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  Diagnoses solely on single RGB camera pixels without knowing humidity or rain.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  Fabricates confident percentages (e.g. "98% Early Blight") when actually uncertain.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  Frequently recommends illegal antibiotic sprays (streptomycin) or dangerous pesticide cocktails.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  Cannot ask clarifying follow-up questions when symptoms overlap.
                </li>
              </ul>
            </div>

            <div className="bg-emerald-950/20 border border-emerald-500/40 rounded-2xl p-6">
              <div className="flex items-center gap-2 text-emerald-400 font-bold mb-4">
                <ShieldCheck className="w-5 h-5" />
                <span>KrishiGuard AI Engine</span>
              </div>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">✓</span>
                  Cross-checks local Open-Meteo microclimate: fungal risk requires &gt;80% humidity.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">✓</span>
                  Flags uncertainty honestly: switches to <code>awaiting_farmer_input</code> when evidence is tied.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">✓</span>
                  Enforces strict chemical safety barriers, organic bio-fungicides (Trichoderma), and PPE warnings.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">✓</span>
                  Links every recommendation directly to verified ICAR and State University bulletins.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Target Crop Focus */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-2xl font-bold text-white mb-3 font-['Outfit']">Initial Focus: Tomato (Solanum lycopersicum)</h2>
        <p className="text-sm text-slate-400 max-w-2xl mx-auto mb-8">
          In strict compliance with hackathon guidelines, we do not claim to diagnose every disease on earth. We focus on rigorous, deep diagnosis of primary tomato conditions:
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {[
            "Early Blight (Alternaria solani)",
            "Late Blight (Phytophthora infestans)",
            "Leaf Mold (Passalora fulva)",
            "Bacterial Spot (Xanthomonas)",
            "Yellow Leaf Curl Virus (TYLCV)",
            "Healthy Tomato Foliage"
          ].map((cond, i) => (
            <span key={i} className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium">
              🌿 {cond}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
};
