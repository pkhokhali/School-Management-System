import { Box, Tab, Tabs } from '@mui/material'
import { ReactNode, useState } from 'react'

type TabItem = { id: string; label: string; panel: ReactNode }

type PageTabsProps = {
  tabs: TabItem[]
  defaultTab?: string
}

export default function PageTabs({ tabs, defaultTab }: PageTabsProps) {
  const [active, setActive] = useState(defaultTab || tabs[0]?.id)
  const panel = tabs.find((t) => t.id === active)?.panel

  return (
    <Box>
      <Tabs
        value={active}
        onChange={(_, v) => setActive(v)}
        sx={{ mb: 2, borderBottom: 1, borderColor: 'divider' }}
      >
        {tabs.map((t) => (
          <Tab key={t.id} value={t.id} label={t.label} sx={{ textTransform: 'none', fontWeight: 600 }} />
        ))}
      </Tabs>
      <Box>{panel}</Box>
    </Box>
  )
}
