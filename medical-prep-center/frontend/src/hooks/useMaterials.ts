import { useState, useEffect, useCallback, useRef } from 'react';
import { materialsAPI, MaterialsAPIError } from '../services/api/materials';
import type { 
  MaterialsData, 
  Section, 
  SearchResult, 
  MaterialsStatistics
} from '../services/api/materials';

// ========== КОНФИГУРАЦИЯ КЭША ==========

const CACHE_CONFIG = {
  defaultExpiry: 24 * 60 * 60 * 1000, // 24 часа
  maxCacheSize: 50,
  keyPrefix: 'materials_cache_'
};

// ========== МЕНЕДЖЕР КЭША ==========

class CacheManager {
  private isValidCache(item: any): boolean {
    return item && 
           item.timestamp && 
           item.data !== null && 
           item.data !== undefined &&
           (Date.now() - item.timestamp < CACHE_CONFIG.defaultExpiry);
  }

  set(key: string, data: any): void {
    if (!data) return; // Не кэшируем пустые данные
    
    try {
      const cacheItem = {
        data,
        timestamp: Date.now(),
        version: '1.0'
      };
      localStorage.setItem(`${CACHE_CONFIG.keyPrefix}${key}`, JSON.stringify(cacheItem));
      this.cleanup();
    } catch (error) {
      console.warn('Ошибка сохранения в кэш:', error);
    }
  }

  get<T>(key: string): T | null {
    try {
      const cached = localStorage.getItem(`${CACHE_CONFIG.keyPrefix}${key}`);
      if (!cached) return null;
      
      const item = JSON.parse(cached);
      if (this.isValidCache(item)) {
        return item.data;
      }
      
      // Удаляем устаревший кэш
      this.remove(key);
      return null;
    } catch (error) {
      console.warn('Ошибка чтения из кэша:', error);
      this.remove(key); // Удаляем поврежденный кэш
      return null;
    }
  }

  remove(key: string): void {
    try {
      localStorage.removeItem(`${CACHE_CONFIG.keyPrefix}${key}`);
    } catch (error) {
      console.warn('Ошибка удаления из кэша:', error);
    }
  }

  clear(): void {
    try {
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith(CACHE_CONFIG.keyPrefix)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn('Ошибка очистки кэша:', error);
    }
  }

  private cleanup(): void {
    try {
      const cacheKeys = Object.keys(localStorage).filter(key => 
        key.startsWith(CACHE_CONFIG.keyPrefix)
      );
      
      if (cacheKeys.length > CACHE_CONFIG.maxCacheSize) {
        const entries = cacheKeys.map(key => {
          try {
            const item = localStorage.getItem(key);
            return {
              key,
              timestamp: item ? JSON.parse(item).timestamp : 0
            };
          } catch {
            return { key, timestamp: 0 };
          }
        }).sort((a, b) => a.timestamp - b.timestamp);

        const toRemove = entries.slice(0, entries.length - CACHE_CONFIG.maxCacheSize);
        toRemove.forEach(entry => localStorage.removeItem(entry.key));
      }
    } catch (error) {
      console.warn('Ошибка очистки кэша:', error);
    }
  }

  getInfo(): { size: number; maxSize: number; usage: string } {
    try {
      const cacheKeys = Object.keys(localStorage).filter(key => 
        key.startsWith(CACHE_CONFIG.keyPrefix)
      );
      
      return {
        size: cacheKeys.length,
        maxSize: CACHE_CONFIG.maxCacheSize,
        usage: `${((cacheKeys.length / CACHE_CONFIG.maxCacheSize) * 100).toFixed(1)}%`
      };
    } catch {
      return { size: 0, maxSize: CACHE_CONFIG.maxCacheSize, usage: '0%' };
    }
  }
}

const cache = new CacheManager();

// ========== МЕНЕДЖЕР UI СОСТОЯНИЯ ==========

type Theme = 'light' | 'dark';
type Language = 'ru' | 'en';

interface UIState {
  selectedSubject: string;
  selectedModule: number | string | null;
  expandedSections: Record<string, boolean>;
  theme: Theme;
  language: Language;
}

class UIStateManager {
  private readonly STORAGE_KEY = 'materials_ui_state';

  getInitialState(): UIState {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          selectedSubject: this.validateSubject(parsed.selectedSubject) || 'chemistry',
          selectedModule: parsed.selectedModule || null,
          expandedSections: parsed.expandedSections || {},
          theme: ['light', 'dark'].includes(parsed.theme) ? parsed.theme : 'light',
          language: ['ru', 'en'].includes(parsed.language) ? parsed.language : 'ru'
        };
      }
    } catch (error) {
      console.warn('Ошибка загрузки состояния UI:', error);
    }
    
    return {
      selectedSubject: 'chemistry',
      selectedModule: null,
      expandedSections: {},
      theme: 'light',
      language: 'ru'
    };
  }

  saveState(state: UIState): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
        ...state,
        selectedSubject: this.validateSubject(state.selectedSubject) || 'chemistry'
      }));
    } catch (error) {
      console.warn('Ошибка сохранения состояния UI:', error);
    }
  }

  private validateSubject(subject: string): string | null {
    const validSubjects = ['chemistry', 'biology'];
    return validSubjects.includes(subject) ? subject : null;
  }
}

const uiStateManager = new UIStateManager();

// ========== ХУКИ ==========

// Хук для материалов
interface UseMaterialsResult {
  data: MaterialsData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  isValidating: boolean;
}

export function useMaterials(subjectName: string): UseMaterialsResult {
  const [data, setData] = useState<MaterialsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const loadMaterials = useCallback(async (forceRefresh = false) => {
    if (!subjectName) {
      setData(null);
      setError(null);
      return;
    }

    const cacheKey = `subject_${subjectName}`;
    
    // Проверяем кэш сначала
    if (!forceRefresh) {
      const cached = cache.get<MaterialsData>(cacheKey);
      if (cached) {
        setData(cached);
        setError(null);
        setLoading(false);
        return;
      }
    }

    // Отменяем предыдущий запрос
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(!forceRefresh || data === null);
    setError(null);
    setIsValidating(forceRefresh && data !== null);

    try {
      // Исправлено: API возвращает объект с materials, а не прямо MaterialsData
      const response = await materialsAPI.getMaterialsBySubject(subjectName);
      
      if (!controller.signal.aborted) {
        // Обработка правильной структуры ответа
        setData(response);
        cache.set(cacheKey, response);
        setError(null);
      }
    } catch (err: unknown) {
      if (!controller.signal.aborted) {
        const errorMessage = err instanceof MaterialsAPIError 
          ? err.message 
          : 'Ошибка загрузки материалов';
        setError(errorMessage);
        
        // Пытаемся загрузить из кэша при ошибке
        if (!forceRefresh) {
          const cached = cache.get<MaterialsData>(cacheKey);
          if (cached) {
            setData(cached);
          }
        }
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
        setIsValidating(false);
      }
    }
  }, [subjectName, data]);

  const refresh = useCallback(async () => {
    await loadMaterials(true);
  }, [loadMaterials]);

  useEffect(() => {
    loadMaterials();
    
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [loadMaterials]);

  return { data, loading, error, refresh, isValidating };
}

// Хук для материалов раздела
export function useSectionMaterials(sectionId: number | null) {
  const [data, setData] = useState<Section | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSection = useCallback(async () => {
    if (!sectionId) {
      setData(null);
      setError(null);
      return;
    }

    const cacheKey = `section_${sectionId}`;
    const cached = cache.get<Section>(cacheKey);
    
    if (cached) {
      setData(cached);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const section = await materialsAPI.getSectionMaterials(sectionId);
      setData(section);
      cache.set(cacheKey, section);
    } catch (err: unknown) {
      const errorMessage = err instanceof MaterialsAPIError 
        ? err.message 
        : 'Ошибка загрузки раздела';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [sectionId]);

  useEffect(() => {
    loadSection();
  }, [loadSection]);

  return { data, loading, error, refresh: loadSection };
}

// Хук для поиска
interface UseSearchResult {
  results: SearchResult[];
  loading: boolean;
  error: string | null;
  search: (query: string, filters?: any) => Promise<void>;
  clearResults: () => void;
}

export function useSearch(): UseSearchResult {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceTimerRef = useRef<number | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const search = useCallback(async (query: string, filters?: {
    subject_filter?: string;
    section_filter?: number;
    limit?: number;
  }) => {
    if (!query || query.trim().length < 2) {
      setResults([]);
      setError(null);
      return;
    }

    // Отменяем предыдущий запрос
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Очищаем предыдущий debounce
    if (debounceTimerRef.current) {
      window.clearTimeout(debounceTimerRef.current);
    }

    // Debounce поиска
    debounceTimerRef.current = window.setTimeout(async () => {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        const searchResults = await materialsAPI.searchMaterials(query.trim(), filters);
        
        if (!controller.signal.aborted) {
          setResults(searchResults);
        }
      } catch (err: unknown) {
        if (!controller.signal.aborted) {
          const errorMessage = err instanceof MaterialsAPIError 
            ? err.message 
            : 'Ошибка поиска';
          setError(errorMessage);
          setResults([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
    setLoading(false);
    
    if (debounceTimerRef.current) {
      window.clearTimeout(debounceTimerRef.current);
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        window.clearTimeout(debounceTimerRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { results, loading, error, search, clearResults };
}

// Хук для UI состояния
export function useUIState() {
  const [uiState, setUIState] = useState<UIState>(() => uiStateManager.getInitialState());

  const updateUIState = useCallback((updates: Partial<UIState>) => {
    setUIState(prev => {
      const newState = { ...prev, ...updates };
      uiStateManager.saveState(newState);
      return newState;
    });
  }, []);

  const setSelectedSubject = useCallback((subject: string) => {
    if (['chemistry', 'biology'].includes(subject)) {
      updateUIState({ selectedSubject: subject, selectedModule: null });
    }
  }, [updateUIState]);

  const setSelectedModule = useCallback((moduleId: number | string | null) => {
    updateUIState({ selectedModule: moduleId });
  }, [updateUIState]);

  const toggleSection = useCallback((sectionId: string) => {
    setUIState(prev => {
      const newExpandedSections = {
        ...prev.expandedSections,
        [sectionId]: !prev.expandedSections[sectionId]
      };
      const newState = { ...prev, expandedSections: newExpandedSections };
      uiStateManager.saveState(newState);
      return newState;
    });
  }, []);

  const setTheme = useCallback((theme: Theme) => {
    updateUIState({ theme });
  }, [updateUIState]);

  const setLanguage = useCallback((language: Language) => {
    updateUIState({ language });
  }, [updateUIState]);

  return {
    uiState,
    updateUIState,
    setSelectedSubject,
    setSelectedModule,
    toggleSection,
    setTheme,
    setLanguage
  };
}

// Хук для статистики
export function useStatistics() {
  const [statistics, setStatistics] = useState<MaterialsStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStatistics = useCallback(async () => {
    const cacheKey = 'statistics';
    const cached = cache.get<MaterialsStatistics>(cacheKey);
    
    if (cached) {
      setStatistics(cached);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const stats = await materialsAPI.getStatistics();
      setStatistics(stats);
      cache.set(cacheKey, stats);
    } catch (err: unknown) {
      const errorMessage = err instanceof MaterialsAPIError 
        ? err.message 
        : 'Ошибка загрузки статистики';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatistics();
  }, [loadStatistics]);

  return { statistics, loading, error, refresh: loadStatistics };
}

// Хук для управления кэшем
export function useCache() {
  const [cacheInfo, setCacheInfo] = useState(() => cache.getInfo());

  const refreshCacheInfo = useCallback(() => {
    setCacheInfo(cache.getInfo());
  }, []);

  const clearCache = useCallback(() => {
    cache.clear();
    refreshCacheInfo();
  }, [refreshCacheInfo]);

  const removeCacheItem = useCallback((key: string) => {
    cache.remove(key);
    refreshCacheInfo();
  }, [refreshCacheInfo]);

  useEffect(() => {
    const interval = setInterval(refreshCacheInfo, 30000);
    return () => clearInterval(interval);
  }, [refreshCacheInfo]);

  return {
    cacheInfo,
    refreshCacheInfo,
    clearCache,
    removeCacheItem
  };
}

// Основной хук страницы материалов
export function useMaterialsPage() {
  const { uiState, setSelectedSubject, setSelectedModule, toggleSection } = useUIState();
  const materials = useMaterials(uiState.selectedSubject);
  const sectionMaterials = useSectionMaterials(
    typeof uiState.selectedModule === 'number' ? uiState.selectedModule : null
  );
  const search = useSearch();
  const { statistics } = useStatistics();
  const cacheManager = useCache();

  // Производные состояния
  const currentData = materials.data?.[uiState.selectedSubject];
  const selectedModuleData = 
    uiState.selectedModule && uiState.selectedModule !== 'all' && currentData
      ? currentData.modules?.find(m => m.id === uiState.selectedModule)
      : null;

  // Обработчики
  const handleSubjectChange = useCallback((subject: string) => {
    setSelectedSubject(subject);
  }, [setSelectedSubject]);

  const handleModuleSelect = useCallback((moduleId: number | string) => {
    setSelectedModule(moduleId);
  }, [setSelectedModule]);

  const handleBackToModules = useCallback(() => {
    setSelectedModule(null);
  }, [setSelectedModule]);

  const handleAllModules = useCallback(() => {
    setSelectedModule('all');
  }, [setSelectedModule]);

  const handleRefresh = useCallback(async () => {
    const promises = [materials.refresh()];
    if (sectionMaterials.refresh) {
      promises.push(sectionMaterials.refresh());
    }
    await Promise.allSettled(promises);
  }, [materials.refresh, sectionMaterials.refresh]);

  // Проверка загрузки
  const isLoading = materials.loading || sectionMaterials.loading;
  const hasError = materials.error || sectionMaterials.error;

  return {
    // Состояние
    uiState,
    currentData,
    selectedModuleData,
    statistics,
    isLoading,
    hasError: hasError ? (materials.error || sectionMaterials.error) : null,

    // Данные
    materials: materials.data,
    sectionMaterials: sectionMaterials.data,
    searchResults: search.results,

    // Состояние загрузки
    materialsLoading: materials.loading,
    materialsValidating: materials.isValidating,
    sectionLoading: sectionMaterials.loading,
    searchLoading: search.loading,

    // Обработчики
    handleSubjectChange,
    handleModuleSelect,
    handleBackToModules,
    handleAllModules,
    handleRefresh,
    toggleSection,

    // Поиск
    search: search.search,
    clearSearch: search.clearResults,
    searchError: search.error,

    // Кэш
    cacheManager
  };
}