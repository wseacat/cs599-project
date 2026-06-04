/**
 * Connect to the SSE streaming chat endpoint.
 * POST /api/chat/stream with fetch, parse SSE events.
 *
 * Supports event types:
 * - progress: agent workflow progress updates
 * - token: answer text chunks
 * - final: complete result with citations
 * - error: error messages
 *
 * @param {string} message
 * @param {number|null} conversationId
 * @param {object} callbacks - { onProgress, onToken, onFinal, onError }
 * @returns {AbortController} - call .abort() to cancel
 */
export function streamChat(message, conversationId, { onProgress, onToken, onFinal, onError }) {
  const controller = new AbortController()
  const token = localStorage.getItem('rag_token')
  let settled = false

  fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, conversation_id: conversationId }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() // keep incomplete line in buffer

        let eventType = ''
        for (const line of lines) {
          if (line.startsWith('event:')) {
            eventType = line.slice(6).trim()
          } else if (line.startsWith('data:')) {
            const data = line.slice(5).trim()
            if (!data) continue
            try {
              const parsed = JSON.parse(data)
              if (eventType === 'progress') {
                onProgress?.(parsed)
              } else if (eventType === 'token') {
                onToken?.(parsed)
              } else if (eventType === 'final') {
                settled = true
                onFinal?.(parsed)
              } else if (eventType === 'error') {
                settled = true
                onError?.(new Error(parsed.detail || parsed.message || 'Stream error'))
              }
            } catch {
              // non-JSON data line, skip
            }
            eventType = ''
          } else if (line.trim() === '') {
            eventType = ''
          }
        }
      }

      // Stream ended without a final event
      if (!settled) {
        onError?.(new Error('Stream ended unexpectedly'))
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError' && !settled) {
        onError?.(err)
      }
    })

  return controller
}
