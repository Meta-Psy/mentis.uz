// ========== КОНСТАНТЫ ==========

export const SEARCH_RESULT_TYPES = {
  TOPIC: 'topic',
  SECTION: 'section', 
  FILE: 'file'
} as const;

export const FILE_TYPES = {
  BOOK: 'book',
  TEST_BOOK: 'test_book'
} as const;

export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark'
} as const;

export const LANGUAGES = {
  RU: 'ru',
  EN: 'en'
} as const;

// ========== ТИПЫ ==========

export type SearchResultType = typeof SEARCH_RESULT_TYPES[keyof typeof SEARCH_RESULT_TYPES];
export type FileType = typeof FILE_TYPES[keyof typeof FILE_TYPES];
export type Theme = typeof THEMES[keyof typeof THEMES];
export type Language = typeof LANGUAGES[keyof typeof LANGUAGES];

export interface DownloadableFile {
  id: number;
  title: string;
  author: string;
  size: string;
  format: string;
  download_url?: string;
}

export interface Topic {
  id: number;
  title: string;
  homework: string[];
  videoUrl: string;
  testId: number;
  block_name?: string;
}

export interface Section {
  id: number;
  name: string;
  description?: string;
  books: DownloadableFile[];
  testBooks: DownloadableFile[];
  topics: Topic[];
}

export interface SubjectData {
  modules: Section[];
}

export interface MaterialsData {
  [subjectName: string]: SubjectData;
}

export interface SearchResult {
  type: SearchResultType;
  id: number;
  title: string;
  description?: string;
  subject_name: string;
  section_name?: string;
}

export interface MaterialsStatistics {
  total_subjects: number;
  total_sections: number;
  total_topics: number;
  total_files: number;
  subjects_breakdown: Record<string, number>;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface APIErrorInterface {
  status?: number;
  code?: string;
  message: string;
}

export interface MaterialsResponseModel {
  materials: MaterialsData;
}

// ========== КОНФИГУРАЦИЯ ==========

const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    const envVar = (window as any).env?.REACT_APP_API_URL;
    if (envVar) return envVar;
  }
  return 'http://localhost:8000/api';
};

const API_CONFIG = {
  baseURL: getApiBaseUrl(),
  timeout: 15000,
  retries: 3,
  retryDelay: 1000
};

// ========== ОШИБКИ ==========

export class MaterialsAPIError extends Error implements APIErrorInterface {
  public status?: number;
  public code?: string;
  public details?: any;

  constructor(
    message: string,
    status?: number,
    code?: string,
    details?: any
  ) {
    super(message);
    this.name = 'MaterialsAPIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// ========== УТИЛИТЫ ==========

const delay = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

const retryRequest = async <T>(
  fn: () => Promise<T>,
  retries: number = API_CONFIG.retries,
  retryDelay: number = API_CONFIG.retryDelay
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && error instanceof MaterialsAPIError && error.status !== 404) {
      await delay(retryDelay);
      return retryRequest(fn, retries - 1, retryDelay * 1.5);
    }
    throw error;
  }
};

// ========== HTTP КЛИЕНТ ==========

class HTTPClient {
  private baseURL: string;
  private timeout: number;

  constructor(baseURL: string, timeout: number = API_CONFIG.timeout) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let details = null;
      
      try {
        if (contentType?.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
          details = errorData;
        } else {
          errorMessage = await response.text() || errorMessage;
        }
      } catch {
        // Игнорируем ошибки парсинга
      }
      
      throw new MaterialsAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new MaterialsAPIError('Некорректный формат ответа от сервера');
    }
  }

  private createAbortController(): AbortController {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    
    controller.signal.addEventListener('abort', () => clearTimeout(timeoutId));
    
    return controller;
  }

  async get<T>(endpoint: string, params?: Record<string, string | number>): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const controller = this.createAbortController();

    try {
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      return this.handleResponse<T>(response);
    } catch (error: unknown) {
      if ((error as any)?.name === 'AbortError') {
        throw new MaterialsAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    const controller = this.createAbortController();

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      return this.handleResponse<T>(response);
    } catch (error: unknown) {
      if ((error as any)?.name === 'AbortError') {
        throw new MaterialsAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== MATERIALS API ==========

export class MaterialsAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/materials`);
  }

  async getMaterialsBySubject(subjectName: string): Promise<MaterialsData> {
    if (!subjectName || typeof subjectName !== 'string') {
      throw new MaterialsAPIError('Название предмета обязательно');
    }

    const normalizedSubject = this.normalizeSubjectName(subjectName);
    
    return retryRequest(async () => {
      try {
        const response = await this.client.get<MaterialsResponseModel>(`/${normalizedSubject}`);
        return response.materials || {};
      } catch (error) {
        if (error instanceof MaterialsAPIError && error.status === 404) {
          return { [normalizedSubject]: { modules: [] } };
        }
        throw error;
      }
    });
  }

  async getSectionMaterials(sectionId: number): Promise<Section> {
    if (!sectionId || sectionId <= 0) {
      throw new MaterialsAPIError('Корректный ID раздела обязателен');
    }

    return retryRequest(async () => {
      return this.client.get<Section>(`/section/${sectionId}`);
    });
  }

  async getTopicDetails(topicId: number): Promise<Topic & { 
    additional_material?: string;
    block_name?: string;
    section_name?: string;
    subject_name?: string;
    number?: number;
    questions_count?: number;
  }> {
    if (!topicId || topicId <= 0) {
      throw new MaterialsAPIError('Корректный ID темы обязателен');
    }

    return retryRequest(async () => {
      return this.client.get(`/topic/${topicId}`);
    });
  }

  async searchMaterials(
    query: string, 
    filters?: { 
      subject_filter?: string;
      section_filter?: number;
      limit?: number;
    }
  ): Promise<SearchResult[]> {
    if (!query || query.trim().length < 2) {
      throw new MaterialsAPIError('Поисковый запрос должен содержать минимум 2 символа');
    }

    const params: Record<string, string | number> = { 
      query: query.trim() 
    };
    
    if (filters?.subject_filter) {
      params.subject_filter = this.normalizeSubjectName(filters.subject_filter);
    }
    if (filters?.section_filter) {
      params.section_filter = filters.section_filter;
    }
    if (filters?.limit && filters.limit > 0) {
      params.limit = Math.min(filters.limit, 100);
    }

    return retryRequest(async () => {
      try {
        return this.client.get<SearchResult[]>('/search', params);
      } catch (error) {
        if (error instanceof MaterialsAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  async getStatistics(): Promise<MaterialsStatistics> {
    return retryRequest(async () => {
      return this.client.get<MaterialsStatistics>('/statistics');
    });
  }

  async addFileToSection(
    sectionId: number, 
    fileData: {
      title: string;
      author: string;
      size: string;
      format: string;
      file_type: FileType;
      url?: string;
    }
  ): Promise<{ status: string; message: string; file_id: number }> {
    if (!sectionId || sectionId <= 0) {
      throw new MaterialsAPIError('Корректный ID раздела обязателен');
    }

    this.validateFileData(fileData);

    return retryRequest(async () => {
      return this.client.post(`/section/${sectionId}/files`, fileData);
    });
  }

  async healthCheck(): Promise<{ status: string; service: string; version: string; timestamp: string }> {
    try {
      return await this.client.get('/health');
    } catch (error) {
      throw new MaterialsAPIError('Сервис материалов недоступен');
    }
  }

  private normalizeSubjectName(subjectName: string): string {
    const subject = subjectName.toLowerCase().trim();
    
    if (subject.includes('химия') || subject.includes('chemistry') || subject === 'chem') {
      return 'chemistry';
    }
    
    if (subject.includes('биология') || subject.includes('biology') || subject === 'bio') {
      return 'biology';
    }
    
    return subject;
  }

  private validateFileData(fileData: {
    title: string;
    author: string;
    size: string;
    format: string;
    file_type: string;
  }): void {
    if (!fileData.title?.trim()) {
      throw new MaterialsAPIError('Название файла обязательно');
    }
    if (!fileData.author?.trim()) {
      throw new MaterialsAPIError('Автор файла обязателен');
    }
    if (!fileData.size?.trim()) {
      throw new MaterialsAPIError('Размер файла обязателен');
    }
    if (!Object.values(FILE_TYPES).includes(fileData.file_type as FileType)) {
      throw new MaterialsAPIError('Тип файла должен быть book или test_book');
    }
  }
}

// ========== ЭКЗЕМПЛЯР API ==========

export const materialsAPI = new MaterialsAPI();
export default materialsAPI;