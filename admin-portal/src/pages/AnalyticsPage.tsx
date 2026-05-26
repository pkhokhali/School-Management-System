import { useEffect, useState } from 'react'
import { GridColDef } from '@mui/x-data-grid'
import { Chip } from '@mui/material'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import api from '../api/client'

const columns: GridColDef[] = [
  { field: 'name', headerName: 'Student', width: 200 },
  {
    field: 'attendance_pct',
    headerName: 'Attendance %',
    width: 130,
    renderCell: (p) => (
      <Chip
        label={`${Number(p.value).toFixed(1)}%`}
        size="small"
        color={p.value < 75 ? 'error' : 'success'}
        variant="outlined"
      />
    ),
  },
  { field: 'avg_marks', headerName: 'Avg marks', width: 100 },
]

export default function AnalyticsPage() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    api.get('/analytics/at-risk/').then((r) => setRows(r.data)).catch(() => setRows([]))
  }, [])
  return (
    <>
      <PageHeader
        title="At-risk students"
        subtitle="Students with low attendance and below-average performance"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Analytics' }]}
      />
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.student_id} />
    </>
  )
}
