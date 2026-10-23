import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { 
  History, 
  Search, 
  Calendar, 
  ArrowRight, 
  CheckCircle, 
  HelpCircle, 
  Clock, 
  FileText,
  Plus
} from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const { data, isLoading } = useQuery({
    queryKey: ['assessments', 1],
    queryFn: () => api.listAssessments(1, 50)
  });

  const items = data?.items || [];

  const filteredItems = items.filter(item => {
    const matchesSearch = 
      (item.primaryCondition || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.farmName || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.growthStage.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <span className="text-xs uppercase font-bold tracking-widest text-emerald-400">Diagnostic Records</span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1 font-['Outfit']">Assessment History</h1>
          <p className="text-sm text-slate-400 mt-0.5">Audit log of all crop assessments evaluated under the Farm Evidence Loop</p>
        </div>

        <Link
          to="/assessments/new"
          className="px-4 py-2.5 rounded-xl text-sm font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          New Assessment
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by condition, farm, or growth stage..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
        >
          <option value="all">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="awaiting_farmer_input">Awaiting Input</option>
          <option value="processing">In Processing</option>
        </select>
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map(n => (
            <div key={n} className="h-20 rounded-xl bg-slate-900/60 animate-pulse border border-slate-800" />
          ))}
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
          <History className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-white">No assessments found</h3>
          <p className="text-xs text-slate-400 mt-1">Try adjusting your search criteria or create a new assessment.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredItems.map(item => (
            <Link
              key={item.id}
              to={`/assessments/${item.id}`}
              className="glass-panel rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 flex items-center justify-between gap-4 transition-all hover:bg-slate-800/40 group"
            >
              <div className="flex items-center gap-4 min-w-0">
                <div className="w-14 h-14 rounded-lg bg-slate-900 border border-slate-800 overflow-hidden shrink-0 flex items-center justify-center">
                  <img
                    src={item.imageUrl}
                    alt="Foliage"
                    className="w-full h-full object-cover"
                    onError={(e) => { (e.target as any).style.display = 'none'; }}
                  />
                  <FileText className="w-6 h-6 text-slate-600" />
                </div>

                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm sm:text-base font-bold text-white group-hover:text-emerald-400 transition-colors truncate">
                      {item.primaryCondition || 'Tomato Foliage Diagnosis'}
                    </h4>
                    {item.certaintyLevel && (
                      <span className="text-[10px] px-2 py-0.5 rounded-md font-semibold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                        {item.certaintyLevel} Certainty
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                    <span className="font-medium text-slate-300">{item.farmName}</span>
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
                {item.status === 'completed' && (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                    Completed
                  </span>
                )}
                {item.status === 'awaiting_farmer_input' && (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                    <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                    Needs Input
                  </span>
                )}
                {item.status === 'processing' && (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
                    Analyzing
                  </span>
                )}
                <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-emerald-400 transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};
