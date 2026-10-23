import { User, Farm, Assessment, AssessmentListItem } from '../types';

let cachedCsrfToken: string | null = null;
let cachedSessionToken: string | null = typeof window !== 'undefined' ? localStorage.getItem('kg_session_id') : null;

export function setCsrfToken(token: string | null) {
  cachedCsrfToken = token;
}

export function getCsrfToken(): string | null {
  return cachedCsrfToken;
}

export function setSessionToken(token: string | null) {
  cachedSessionToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('kg_session_id', token);
    } else {
      localStorage.removeItem('kg_session_id');
    }
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // Attach session token in headers for resilient cross-origin support
  if (cachedSessionToken) {
    headers.set('Authorization', `Bearer ${cachedSessionToken}`);
    headers.set('X-Session-ID', cachedSessionToken);
  }

  // Attach CSRF token on mutating operations
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method?.toUpperCase() || '')) {
    if (cachedCsrfToken) {
      headers.set('X-CSRF-Token', cachedCsrfToken);
    }
  }

  const defaultProdApi = typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')
    ? 'https://ptw-3ajs.onrender.com'
    : '';
  const baseUrl = import.meta.env.VITE_API_BASE_URL || defaultProdApi;
  const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include' // include session cookie
  });

  const contentType = response.headers.get('content-type') || '';
  let data: any = null;
  if (contentType.includes('application/json')) {
    data = await response.json().catch(() => null);
  } else {
    const text = await response.text().catch(() => '');
    if (text.trim().startsWith('{')) {
      try {
        data = JSON.parse(text);
      } catch {
        data = null;
      }
    }
  }

  if (!response.ok) {
    const errorMsg = data?.error?.message || response.statusText || 'Request failed';
    const errorObj = new Error(errorMsg) as any;
    errorObj.code = data?.error?.code;
    errorObj.status = response.status;
    errorObj.details = data?.error?.details;
    throw errorObj;
  }

  if (!data || typeof data !== 'object') {
    throw new Error('API server returned an empty or invalid response. Please ensure backend is reachable at ' + (baseUrl || 'server'));
  }

  return (typeof data === 'object' && 'data' in data) ? data.data : data;
}

export const api = {
  // Authentication
  async register(payload: { name: string; email: string; password: string; confirm_password: string }) {
    const res = await request<{ user: User; csrfToken: string; sessionId?: string }>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    setCsrfToken(res.csrfToken);
    if (res.sessionId) setSessionToken(res.sessionId);
    return res;
  },

  async login(payload: { email: string; password: string }) {
    const res = await request<{ user: User; csrfToken: string; sessionId?: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    setCsrfToken(res.csrfToken);
    if (res.sessionId) setSessionToken(res.sessionId);
    return res;
  },

  async demoLogin() {
    const res = await request<{ user: User; csrfToken: string; sessionId?: string }>('/api/v1/auth/demo', {
      method: 'POST'
    });
    setCsrfToken(res.csrfToken);
    if (res.sessionId) setSessionToken(res.sessionId);
    return res;
  },

  async logout() {
    await request<boolean>('/api/v1/auth/logout', { method: 'POST' }).catch(() => null);
    setCsrfToken(null);
    setSessionToken(null);
  },

  async getMe() {
    const res = await request<{ user: User; csrfToken: string }>('/api/v1/auth/me');
    setCsrfToken(res.csrfToken);
    return res;
  },

  async changePassword(payload: { current_password: string; new_password: string; confirm_password: string }) {
    return request<boolean>('/api/v1/auth/password/change', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Farms
  async listFarms(): Promise<Farm[]> {
    return request<Farm[]>('/api/v1/farms');
  },

  async createFarm(payload: {
    name: string;
    location: { latitude: number; longitude: number; address?: string; district?: string; state?: string };
    cropTypes: string[];
    sizeInAcres?: number;
  }): Promise<Farm> {
    return request<Farm>('/api/v1/farms', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async getFarm(farmId: string): Promise<Farm> {
    return request<Farm>(`/api/v1/farms/${farmId}`);
  },

  async deleteFarm(farmId: string): Promise<boolean> {
    return request<boolean>(`/api/v1/farms/${farmId}`, { method: 'DELETE' });
  },

  // Assessments
  async createAssessment(formData: FormData): Promise<Assessment> {
    return request<Assessment>('/api/v1/assessments', {
      method: 'POST',
      body: formData
    });
  },

  async listAssessments(page = 1, pageSize = 20): Promise<{ items: AssessmentListItem[]; total: number; has_more: boolean }> {
    return request<{ items: AssessmentListItem[]; total: number; has_more: boolean }>(
      `/api/v1/assessments?page=${page}&page_size=${pageSize}`
    );
  },

  async getAssessment(assessmentId: string): Promise<Assessment> {
    return request<Assessment>(`/api/v1/assessments/${assessmentId}`);
  },

  async submitFollowup(assessmentId: string, answer: string): Promise<Assessment> {
    return request<Assessment>(`/api/v1/assessments/${assessmentId}/followups`, {
      method: 'POST',
      body: JSON.stringify({ answer })
    });
  },

  async deleteAssessment(assessmentId: string): Promise<boolean> {
    return request<boolean>(`/api/v1/assessments/${assessmentId}`, { method: 'DELETE' });
  },

  // Health & Evaluation Readiness
  async getHealth() {
    return request<{ status: string; services: Record<string, string> }>('/api/v1/health/ready');
  },

  async getEvaluationReport() {
    return request<any>('/api/v1/health/evaluation');
  }
};
