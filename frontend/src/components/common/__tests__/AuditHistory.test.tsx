import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { AuditHistory } from '../AuditHistory'
import type { AuditLogResponse } from '@/api'

describe('AuditHistory', () => {
  const mockAuditLogs: AuditLogResponse[] = [
    {
      id: '1',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'created',
      old_values: null,
      new_values: {
        contract_type: 'fixed_monthly',
        rate_amount: '5000.00',
        rate_currency: 'USD',
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T10:00:00Z',
      created_at: '2025-12-08T10:00:00Z',
    },
    {
      id: '2',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'updated',
      old_values: {
        rate_amount: '5000.00',
      },
      new_values: {
        rate_amount: '6000.00',
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T11:00:00Z',
      created_at: '2025-12-08T11:00:00Z',
    },
  ]

  it('should render loading state', () => {
    render(<AuditHistory auditLogs={[]} isLoading={true} />)
    expect(screen.getByText('Loading history...')).toBeInTheDocument()
  })

  it('should render empty state when no logs', () => {
    render(<AuditHistory auditLogs={[]} isLoading={false} />)
    expect(screen.getByText('No history available')).toBeInTheDocument()
    expect(
      screen.getByText('No changes have been recorded for this entity yet.')
    ).toBeInTheDocument()
  })

  it('should render audit log entries', () => {
    render(<AuditHistory auditLogs={mockAuditLogs} isLoading={false} />)
    expect(screen.getByText('Change History')).toBeInTheDocument()
    expect(screen.getByText(/Showing 2 events/)).toBeInTheDocument()
  })

  it('should display action badges with correct text', () => {
    render(<AuditHistory auditLogs={mockAuditLogs} isLoading={false} />)
    expect(screen.getByText('CREATED')).toBeInTheDocument()
    expect(screen.getByText('UPDATED')).toBeInTheDocument()
  })

  it('should display changed by information', () => {
    render(<AuditHistory auditLogs={mockAuditLogs} isLoading={false} />)
    const changedByElements = screen.getAllByText('admin@example.com')
    expect(changedByElements).toHaveLength(2)
  })

  it('should format field names correctly', () => {
    render(<AuditHistory auditLogs={mockAuditLogs} isLoading={false} />)
    expect(screen.getByText('Contract Type:')).toBeInTheDocument()
    expect(screen.getAllByText('Rate Amount:').length).toBeGreaterThan(0)
    expect(screen.getByText('Rate Currency:')).toBeInTheDocument()
  })

  it('should show new values for creation action', () => {
    render(<AuditHistory auditLogs={[mockAuditLogs[0]]} isLoading={false} />)
    expect(screen.getByText('fixed_monthly')).toBeInTheDocument()
    expect(screen.getByText('5000.00')).toBeInTheDocument()
    expect(screen.getByText('USD')).toBeInTheDocument()
  })

  it('should show before/after for update action', () => {
    render(<AuditHistory auditLogs={[mockAuditLogs[1]]} isLoading={false} />)
    expect(screen.getByText(/Changed from/)).toBeInTheDocument()
    expect(screen.getByText(/5000.00/)).toBeInTheDocument()
    expect(screen.getByText(/6000.00/)).toBeInTheDocument()
  })

  it('should handle non-array auditLogs gracefully', () => {
    // @ts-expect-error Testing invalid input
    render(<AuditHistory auditLogs={null} isLoading={false} />)
    expect(screen.getByText('No history available')).toBeInTheDocument()
  })

  it('should handle undefined auditLogs with default value', () => {
    // @ts-expect-error Testing undefined input
    render(<AuditHistory auditLogs={undefined} isLoading={false} />)
    expect(screen.getByText('No history available')).toBeInTheDocument()
  })

  it('should display deletion entries', () => {
    const deletedLog: AuditLogResponse = {
      id: '3',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'deleted',
      old_values: {
        contract_type: 'fixed_monthly',
        rate_amount: '5000.00',
      },
      new_values: null,
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T12:00:00Z',
      created_at: '2025-12-08T12:00:00Z',
    }

    render(<AuditHistory auditLogs={[deletedLog]} isLoading={false} />)
    expect(screen.getByText('Entity deleted')).toBeInTheDocument()
  })

  it('should handle metadata display', () => {
    const logWithMetadata: AuditLogResponse = {
      ...mockAuditLogs[0],
      metadata: { reason: 'Annual review', approved_by: 'manager@example.com' },
    }

    render(<AuditHistory auditLogs={[logWithMetadata]} isLoading={false} />)
    expect(screen.getByText('Additional metadata')).toBeInTheDocument()
  })

  it('should not display metadata section when empty', () => {
    render(<AuditHistory auditLogs={[mockAuditLogs[0]]} isLoading={false} />)
    expect(screen.queryByText('Additional metadata')).not.toBeInTheDocument()
  })

  it('should handle null values in changes', () => {
    const logWithNulls: AuditLogResponse = {
      id: '4',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'updated',
      old_values: {
        description: null,
      },
      new_values: {
        description: 'New description',
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T13:00:00Z',
      created_at: '2025-12-08T13:00:00Z',
    }

    render(<AuditHistory auditLogs={[logWithNulls]} isLoading={false} />)
    expect(screen.getByText(/Set to/)).toBeInTheDocument()
    expect(screen.getByText(/New description/)).toBeInTheDocument()
  })

  it('should handle removal of values', () => {
    const logWithRemoval: AuditLogResponse = {
      id: '5',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'updated',
      old_values: {
        description: 'Old description',
      },
      new_values: {
        description: null,
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T14:00:00Z',
      created_at: '2025-12-08T14:00:00Z',
    }

    render(<AuditHistory auditLogs={[logWithRemoval]} isLoading={false} />)
    expect(screen.getByText(/Removed from/)).toBeInTheDocument()
  })

  it('should display singular "event" for one log', () => {
    render(<AuditHistory auditLogs={[mockAuditLogs[0]]} isLoading={false} />)
    expect(screen.getByText(/Showing 1 event$/)).toBeInTheDocument()
  })

  it('should display plural "events" for multiple logs', () => {
    render(<AuditHistory auditLogs={mockAuditLogs} isLoading={false} />)
    expect(screen.getByText(/Showing 2 events/)).toBeInTheDocument()
  })

  it('should handle complex object changes', () => {
    const logWithObjects: AuditLogResponse = {
      id: '6',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'updated',
      old_values: {
        benefits: { health: true, dental: false },
      },
      new_values: {
        benefits: { health: true, dental: true },
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T15:00:00Z',
      created_at: '2025-12-08T15:00:00Z',
    }

    render(<AuditHistory auditLogs={[logWithObjects]} isLoading={false} />)
    expect(screen.getByText(/Changed from/)).toBeInTheDocument()
  })

  it('should not show changes when no fields changed', () => {
    const logNoChange: AuditLogResponse = {
      id: '7',
      entity_type: 'contract',
      entity_id: 'contract-1',
      employee_id: 'emp-1',
      action: 'updated',
      old_values: {
        rate_amount: '5000.00',
      },
      new_values: {
        rate_amount: '5000.00',
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-12-08T16:00:00Z',
      created_at: '2025-12-08T16:00:00Z',
    }

    render(<AuditHistory auditLogs={[logNoChange]} isLoading={false} />)
    expect(screen.getByText('No changes detected')).toBeInTheDocument()
  })
})
