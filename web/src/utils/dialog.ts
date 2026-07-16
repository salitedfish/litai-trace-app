import { createVNode, render } from 'vue'
import Toast from '../components/ui/Toast.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export const showToast = (message: string, type: ToastType = 'info', duration = 3000) => {
  const container = document.createElement('div')
  document.body.appendChild(container)

  const vnode = createVNode(Toast, {
    message,
    type,
    duration,
    onClose: () => {
      render(null, container)
      if (container.parentNode) {
        container.parentNode.removeChild(container)
      }
    }
  })

  render(vnode, container)
}

export const showConfirm = (message: string, title?: string): Promise<boolean> => {
  return new Promise((resolve) => {
    const container = document.createElement('div')
    document.body.appendChild(container)

    const vnode = createVNode(ConfirmDialog, {
      title,
      message,
      onResolve: resolve,
      onClose: () => {
        render(null, container)
        if (container.parentNode) {
          container.parentNode.removeChild(container)
        }
      }
    })

    render(vnode, container)
  })
}
