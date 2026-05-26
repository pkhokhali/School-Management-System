import { GridActionsCellItem, GridRowParams } from '@mui/x-data-grid'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined'

type GridActionsProps<T = Record<string, unknown>> = {
  onEdit?: (row: T) => void
  onView?: (row: T) => void
  onDelete?: (row: T) => void
  canEdit?: boolean
  canView?: boolean
  canDelete?: boolean
}

export function buildActionColumns<T = Record<string, unknown>>({
  onEdit,
  onView,
  onDelete,
  canEdit = true,
  canView = false,
  canDelete = false,
}: GridActionsProps<T>) {
  if (!canEdit && !canDelete && !canView) return []
  return [
    {
      field: 'actions',
      type: 'actions' as const,
      headerName: 'Actions',
      width: canView && canEdit && canDelete ? 130 : canView && canEdit ? 120 : canEdit && canDelete ? 100 : 90,
      getActions: (params: GridRowParams) => {
        const actions = []
        if (canView && onView) {
          actions.push(
            <GridActionsCellItem
              key="view"
              icon={<VisibilityOutlinedIcon />}
              label="View"
              onClick={() => onView(params.row as T)}
            />,
          )
        }
        if (canEdit && onEdit) {
          actions.push(
            <GridActionsCellItem
              key="edit"
              icon={<EditOutlinedIcon />}
              label="Edit"
              onClick={() => onEdit(params.row as T)}
            />,
          )
        }
        if (canDelete && onDelete) {
          actions.push(
            <GridActionsCellItem
              key="delete"
              icon={<DeleteOutlineIcon />}
              label="Delete"
              onClick={() => onDelete(params.row as T)}
            />,
          )
        }
        return actions
      },
    },
  ]
}
