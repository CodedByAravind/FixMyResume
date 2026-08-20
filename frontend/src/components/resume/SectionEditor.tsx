import { useState } from 'react'

interface FieldConfig {
  key: string
  label: string
  type?: string
  placeholder?: string
  required?: boolean
  span?: boolean
}

interface SectionEditorProps {
  title: string
  entries: Array<Record<string, any> & { id: number }>
  fields: FieldConfig[]
  onCreate: (data: Record<string, unknown>) => Promise<{ id: number }>
  onUpdate: (id: number, data: Record<string, unknown>) => Promise<unknown>
  onDelete: (id: number) => Promise<void>
}

interface Row {
  id?: number
  values: Record<string, string>
}

function SectionEditor({ title, entries, fields, onCreate, onUpdate, onDelete }: SectionEditorProps) {
  const [rows, setRows] = useState<Row[]>(() =>
    entries.map((entry) => {
      const values: Record<string, string> = {}
      for (const f of fields) values[f.key] = String(entry[f.key] ?? '')
      return { id: entry.id, values }
    }),
  )
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const blankValues = (): Record<string, string> => {
    const values: Record<string, string> = {}
    for (const f of fields) values[f.key] = ''
    return values
  }

  const updateValue = (index: number, key: string, value: string) => {
    setRows((prev) =>
      prev.map((row, i) => (i === index ? { ...row, values: { ...row.values, [key]: value } } : row)),
    )
  }

  const addRow = () => {
    setError(null)
    setRows((prev) => [...prev, { id: undefined, values: blankValues() }])
  }

  const saveRow = async (index: number) => {
    const row = rows[index]
    const data: Record<string, string> = { ...row.values }
    for (const key of Object.keys(data)) {
      if (data[key].trim() === '') delete data[key]
    }
    setError(null)
    setBusy(row.id ? `up-${row.id}` : 'new')
    try {
      if (row.id) {
        await onUpdate(row.id, data)
      } else {
        const created = await onCreate(data)
        setRows((prev) => prev.map((r, i) => (i === index ? { ...r, id: created.id } : r)))
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to save entry')
    } finally {
      setBusy(null)
    }
  }

  const removeRow = async (index: number) => {
    const row = rows[index]
    setError(null)
    setBusy(row.id ? `del-${row.id}` : 'new')
    try {
      if (row.id) await onDelete(row.id)
      setRows((prev) => prev.filter((_, i) => i !== index))
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete entry')
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
        <button onClick={addRow} className="bg-blue-600 text-white rounded-md px-3 py-1.5 text-sm hover:bg-blue-700">
          + Add
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {rows.length === 0 && <p className="text-gray-500 text-sm">No entries yet.</p>}

      <div className="space-y-4">
        {rows.map((row, index) => (
          <div key={row.id ?? `new-${index}`} className="border border-gray-200 rounded-md p-4">
            <div className={`grid gap-3 ${row.values.description !== undefined ? 'md:grid-cols-2' : 'md:grid-cols-2'}`}>
              {fields.map((f) => (
                <div key={f.key} className={f.span ? 'md:col-span-2' : ''}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">{f.label}</label>
                  {f.type === 'textarea' ? (
                    <textarea
                      value={row.values[f.key]}
                      onChange={(e) => updateValue(index, f.key, e.target.value)}
                      placeholder={f.placeholder}
                      rows={3}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <input
                      type={f.type || 'text'}
                      value={row.values[f.key]}
                      onChange={(e) => updateValue(index, f.key, e.target.value)}
                      placeholder={f.placeholder}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-end space-x-2 mt-3">
              <button
                onClick={() => removeRow(index)}
                disabled={busy === `del-${row.id}`}
                className="bg-red-100 text-red-700 rounded-md px-3 py-1.5 text-sm hover:bg-red-200 disabled:opacity-50"
              >
                {busy === `del-${row.id}` ? 'Deleting...' : 'Delete'}
              </button>
              <button
                onClick={() => saveRow(index)}
                disabled={busy === `up-${row.id}` || busy === 'new'}
                className="bg-blue-600 text-white rounded-md px-3 py-1.5 text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {busy === `up-${row.id}` || busy === 'new' ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SectionEditor
