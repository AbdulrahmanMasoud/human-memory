import { ref, watchEffect } from 'vue'

const theme = ref<'dark' | 'light'>(
  (typeof localStorage !== 'undefined' && localStorage.getItem('theme') as 'dark' | 'light') || 'dark'
)

watchEffect(() => {
  document.documentElement.classList.toggle('dark', theme.value === 'dark')
  document.documentElement.classList.toggle('light', theme.value === 'light')
  localStorage.setItem('theme', theme.value)
})

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  return { theme, toggle }
}
