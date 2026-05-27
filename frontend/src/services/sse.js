/**
 * Connect to the SSE streaming chat endpoint.
 * POST /api/chat/stream with fetch, parse SSE events.
 *
 * @param {string} message
 * @param {number|null} conversationId
 * @param {object} callbacks - { onToken, onFinal, onError }
 * @returns {AbortController} - call .abort() to cancel
 */
export function streamChat(message, conversationId, { onToken, onFinal, onError }) {
  const controller = new AbortController()
  const token = localStorage.getItem('rag_token')

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
              if (eventType === 'token') {
                onToken?.(parsed)
              } else if (eventType === 'final') {
                onFinal?.(parsed)
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
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError?.(err)
      }
    })

  return controller
}
