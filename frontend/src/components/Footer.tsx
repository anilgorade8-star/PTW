import React from 'react';
import { ShieldCheck, Sprout, ExternalLink } from 'lucide-react';
import { QualityBadge } from './QualityBadge';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/70 text-slate-400 py-12 mt-20 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & mission */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
                <Sprout className="w-5 h-5 text-emerald-400" />
              </div>
              <span className="text-lg font-bold text-white font-['Outfit']">
                KrishiGuard <span className="text-emerald-400">AI</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-md leading-relaxed">
              Empowering farmers with the <strong>Farm Evidence Loop</strong> — unifying crop photographs, verified farm microclimate weather, and peer-reviewed ICAR agricultural science to prevent crop loss.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400/90 pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Safety Barriers Enforced: No hazardous chemical cocktails or unverified dosages.</span>
            </div>
          </div>

          {/* Agricultural Authorities */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Reviewed Sources</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://www.iihr.res.in"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
                >
                  ICAR - IIHR Bangalore <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a
                  href="https://agritech.tnau.ac.in"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
                >
                  TNAU Agritech Portal <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.pau.edu"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
                >
                  PAU Extension Bulletins <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.iari.res.in"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
                >
                  ICAR - IARI New Delhi <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
            </ul>
          </div>

          {/* Platform Standards */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Core Pillars</h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              <li>• Argon2id & Redis Session Security</li>
              <li>• Microclimate Cache-Aside via Open-Meteo</li>
              <li>• Google Gemini Multimodal Reasoning</li>
              <li>• Deterministic Decision & Uncertainty Engine</li>
              <li>• Private Storage & Ownership Isolation</li>
            </ul>
          </div>
        </div>

        {/* Hackathon Evaluation Readiness Watermark Badge */}
        <QualityBadge />

        <div className="mt-8 pt-6 border-t border-slate-800/60 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500">
          <p>© 2026 KrishiGuard AI. Built for sustainable agriculture and prompt engineering excellence.</p>
          <p className="mt-2 sm:mt-0 text-slate-400">
            For critical outbreaks, always consult your nearest <strong>Krishi Vigyan Kendra (KVK)</strong>.
          </p>
        </div>
      </div>
    </footer>
  );
};
