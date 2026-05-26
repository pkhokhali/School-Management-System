import { Paper } from '@mui/material'
import { DataGrid, DataGridProps } from '@mui/x-data-grid'
import { ReactNode } from 'react'

type DataTableProps = DataGridProps & {
  children?: never
}

export default function DataTable(props: DataTableProps) {
  return (
    <Paper elevation={0} sx={{ borderRadius: 3, overflow: 'hidden' }}>
      <DataGrid
        {...props}
        autoHeight
        disableRowSelectionOnClick
        pageSizeOptions={[10, 20, 50]}
        sx={{
          border: 'none',
          '& .MuiDataGrid-cell:focus': { outline: 'none' },
          ...props.sx,
        }}
      />
    </Paper>
  )
}
