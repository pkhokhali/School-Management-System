import { create } from 'zustand'
import api from '../api/client'

interface FeatureState {
  flags: Record<string, boolean>
  loaded: boolean
  fetchFeatures: () => Promise<void>
  isEnabled: (key: string) => boolean
}

export const useFeatureStore = create<FeatureState>((set, get) => ({
  flags: {},
  loaded: false,
  fetchFeatures: async () => {
    const { data } = await api.get('/features/')
    set({ flags: data.feature_flags, loaded: true })
  },
  isEnabled: (key) => get().flags[key] ?? false,
}))
