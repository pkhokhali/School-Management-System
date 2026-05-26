import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UiState {
  darkMode: boolean
  toggleDarkMode: () => void
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      darkMode: false,
      toggleDarkMode: () => set((s) => ({ darkMode: !s.darkMode })),
    }),
    { name: 'ui-storage' },
  ),
)
