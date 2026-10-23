import { User, Farm, Assessment, AssessmentListItem } from '../types';

let cachedCsrfToken: string | null = null;

export function setCsrfToken(token: string | null) {
  cachedCsrfToken = token;
}

export function getCsrfToken(): string | null {
  return cachedCsrfToken;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // Attach CSRF token on mutating operations
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method?.toUpperCase() || '')) {
    if (cachedCsrfToken) {
      headers.set('X-CSRF-Token', cachedCsrfToken);
    }
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
    credentials: 'include' // include session cookie
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMsg = data?.error?.message || response.statusText || 'Request failed';
    const errorObj = new Error(errorMsg) as any;
    errorObj.code = data?.error?.code;
    errorObj.status = response.status;
    errorObj.details = data?.error?.details;
    throw errorObj;
  }

  return data.data;
}

export const api = {
  // Authentication
  async register(payload: { name: string; email: string; password: string; confirm_password: string }) {
    const res = await request<{ user: User; csrfToken: string }>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    setCsrfToken(res.csrfToken);
    return res;
  },

  async login(payload: { email: string; password: string }) {
    const res = await request<{ user: User; csrfToken: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    setCsrfToken(res.csrfToken);
    return res;
  },

  async logout() {
    await request<boolean>('/api/v1/auth/logout', { method: 'POST' });
    setCsrfToken(null);
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

  // Health
  async getHealth() {
    return request<{ status: string; services: Record<string, string> }>('/api/v1/health/ready');
  }
};
