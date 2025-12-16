import { format, parseISO } from 'date-fns'
import {
  DATE_FORMAT,
  DATETIME_FORMAT,
  DISPLAY_DATE_FORMAT,
  DISPLAY_DATETIME_FORMAT,
  DEFAULT_CURRENCY,
} from './constants'

/**
 * Format a date for display
 */
export function formatDate(date: Date | string | null | undefined): string {
  if (!date) return '-'
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, DISPLAY_DATE_FORMAT)
}

/**
 * Format a datetime for display
 */
export function formatDateTime(date: Date | string | null | undefined): string {
  if (!date) return '-'
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, DISPLAY_DATETIME_FORMAT)
}

/**
 * Format a date for API (ISO format)
 */
export function formatDateForAPI(date: Date | string | null | undefined): string | null {
  if (!date) return null
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, DATE_FORMAT)
}

/**
 * Format a datetime for API (ISO format)
 */
export function formatDateTimeForAPI(date: Date | string | null | undefined): string | null {
  if (!date) return null
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, DATETIME_FORMAT)
}

/**
 * Format currency amount
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  currency: string = DEFAULT_CURRENCY
): string {
  if (amount === null || amount === undefined) return '-'

  const numericAmount = typeof amount === 'string' ? parseFloat(amount) : amount

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numericAmount)
}

/**
 * Format number with thousands separator
 */
export function formatNumber(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return '-'

  const numericValue = typeof value === 'string' ? parseFloat(value) : value

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(numericValue)
}

/**
 * Format percentage
 */
export function formatPercentage(
  value: number | string | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined) return '-'

  const numericValue = typeof value === 'string' ? parseFloat(value) : value

  return `${numericValue.toFixed(decimals)}%`
}

/**
 * Format phone number (basic format)
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return '-'

  // Remove all non-numeric characters
  const cleaned = phone.replace(/\D/g, '')

  // Format as (XXX) XXX-XXXX for US numbers
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
  }

  // Return original if not standard format
  return phone
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string | null | undefined, maxLength: number = 50): string {
  if (!text) return '-'

  if (text.length <= maxLength) return text

  return `${text.slice(0, maxLength)}...`
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes || bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * Capitalize first letter
 */
export function capitalize(text: string | null | undefined): string {
  if (!text) return ''
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}

/**
 * Convert snake_case to Title Case
 */
export function snakeToTitle(text: string | null | undefined): string {
  if (!text) return ''
  return text
    .split('_')
    .map((word) => capitalize(word))
    .join(' ')
}

/**
 * Format duration in hours
 */
export function formatHours(hours: number | null | undefined): string {
  if (hours === null || hours === undefined) return '-'

  if (hours === 0) return '0h'
  if (hours < 1) return `${(hours * 60).toFixed(0)}m`

  const wholeHours = Math.floor(hours)
  const minutes = Math.round((hours - wholeHours) * 60)

  if (minutes === 0) return `${wholeHours}h`
  return `${wholeHours}h ${minutes}m`
}

/**
 * Get initials from name
 */
export function getInitials(name: string | null | undefined): string {
  if (!name) return '?'

  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()

  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
}
